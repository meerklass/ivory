import threading
import time

import psutil


def _aggregate_rss_bytes(process: psutil.Process) -> int:
    """Sum RSS of `process` and all its live children, recursively.

    Silently skips any process that disappears or is inaccessible mid-poll.
    """
    try:
        children = process.children(recursive=True)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        children = []
    total = 0
    for p in [process, *children]:
        try:
            total += p.memory_info().rss
        except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
            continue
    return total


def _aggregate_cpu_seconds(process: psutil.Process) -> float:
    """CPU seconds used so far by `process` and all its descendants, live or finished.

    For each live process in the tree this adds its own user and system time and the
    `children_*` time the kernel has credited it with for descendants it has already waited
    for. A descendant is either live, and counted itself, or finished and waited for, and
    counted in its parent's `children_*`, so nothing is counted twice. A process that
    disappears or is inaccessible mid-poll is skipped; the time of one that has exited but
    not yet been waited for is missed until its parent waits for it.
    """
    try:
        children = process.children(recursive=True)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        children = []
    total = 0.0
    for p in [process, *children]:
        try:
            times = p.cpu_times()
        except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
            continue
        total += times.user + times.system + times.children_user + times.children_system
    return total


class ResourceSampler:
    """Context manager that polls memory and CPU of `process` and all its child
    processes on a background thread while the wrapped block runs.

    CPU is measured from the CPU seconds of the whole process tree, so work done in
    `joblib`/`loky` worker processes counts, not only the main process. 100% is one fully
    used core.

    Usage:
        sampler = ResourceSampler(process)
        with sampler:
            plugin.run(...)
        avg_mem, peak_mem = sampler.avg_memory_gb, sampler.peak_memory_gb
    """

    def __init__(self, process: psutil.Process, interval: float = 0.3):
        self.process = process
        self.interval = interval
        self.memory_samples: list[float] = []
        self.cpu_samples: list[float] = []
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._start_cpu_seconds = 0.0
        self._start_wall = 0.0
        self._last_cpu_seconds = 0.0
        self._last_wall = 0.0

    def _sample(self):
        self.memory_samples.append(_aggregate_rss_bytes(self.process) / (1024**3))
        cpu_seconds, wall = _aggregate_cpu_seconds(self.process), time.monotonic()
        elapsed = wall - self._last_wall
        if elapsed > 0:
            # A process vanishing between two polls can make the difference negative
            used = max(0.0, cpu_seconds - self._last_cpu_seconds)
            self.cpu_samples.append(100.0 * used / elapsed)
        self._last_cpu_seconds, self._last_wall = cpu_seconds, wall

    def _poll_loop(self):
        while not self._stop_event.is_set():
            self._stop_event.wait(self.interval)
            self._sample()

    def __enter__(self):
        self._stop_event.clear()
        self.memory_samples = []
        self.cpu_samples = []
        self._start_cpu_seconds = _aggregate_cpu_seconds(self.process)
        self._start_wall = time.monotonic()
        self._last_cpu_seconds, self._last_wall = (
            self._start_cpu_seconds,
            self._start_wall,
        )
        self.memory_samples.append(_aggregate_rss_bytes(self.process) / (1024**3))
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=self.interval * 2)
        # final sample, in case the run was shorter than one interval; deliberately
        # catch-all so a psutil error here never masks a real exception from the
        # `with` body (e.g. a plugin failure)
        try:
            self._sample()
        except Exception:  # noqa: BLE001
            pass

    @property
    def avg_memory_gb(self) -> float:
        return (
            sum(self.memory_samples) / len(self.memory_samples)
            if self.memory_samples
            else 0.0
        )

    @property
    def peak_memory_gb(self) -> float:
        return max(self.memory_samples) if self.memory_samples else 0.0

    @property
    def avg_cpu_percent(self) -> float:
        """CPU seconds used over the whole block divided by its wall time, in %.

        Taken from the two ends rather than as a mean of the per-poll samples, which would
        weight the short final interval as much as a full one.
        """
        elapsed = self._last_wall - self._start_wall
        if not self.cpu_samples or elapsed <= 0:
            return 0.0
        used = max(0.0, self._last_cpu_seconds - self._start_cpu_seconds)
        return 100.0 * used / elapsed

    @property
    def peak_cpu_percent(self) -> float:
        return max(self.cpu_samples) if self.cpu_samples else 0.0
