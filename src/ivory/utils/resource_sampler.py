import threading
import time

import psutil


def _process_tree(process: psutil.Process) -> list[psutil.Process]:
    """`process` and all its live children, recursively; `process` alone if the lookup fails.

    One call scans the whole process table of the machine (psutil reads every `/proc/<pid>/stat`
    to build the parent map), tens of milliseconds on a busy node, so a poll makes it once and
    hands the list to both aggregates.
    """
    try:
        return [process, *process.children(recursive=True)]
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return [process]


def _aggregate_rss_bytes(
    process: psutil.Process, tree: list[psutil.Process] | None = None
) -> int:
    """Sum RSS of `process` and all its live children, recursively.

    Silently skips any process that disappears or is inaccessible mid-poll.
    :param tree: the process tree from `_process_tree`, looked up here if not given
    """
    total = 0
    for p in tree if tree is not None else _process_tree(process):
        try:
            total += p.memory_info().rss
        except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
            continue
    return total


def _aggregate_cpu_seconds(
    process: psutil.Process, tree: list[psutil.Process] | None = None
) -> float:
    """CPU seconds used so far by `process` and all its descendants, live or finished.

    For each live process in the tree this adds its own user and system time and the
    `children_*` time the kernel has credited it with for descendants it has already waited
    for. A descendant is either live, and counted itself, or finished and waited for, and
    counted in its parent's `children_*`, so nothing is counted twice. A process that
    disappears or is inaccessible mid-poll is skipped; the time of one that has exited but
    not yet been waited for is missed until its parent waits for it.
    :param tree: the process tree from `_process_tree`, looked up here if not given
    """
    total = 0.0
    for p in tree if tree is not None else _process_tree(process):
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

    The poll interval defaults to one second: each poll scans the machine's process table once, and
    the per-plugin averages and peaks do not need more.

    Usage:
        sampler = ResourceSampler(process)
        with sampler:
            plugin.run(...)
        avg_mem, peak_mem = sampler.avg_memory_gb, sampler.peak_memory_gb
    """

    def __init__(self, process: psutil.Process, interval: float = 1.0):
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
        # one scan of the process table per poll; it runs in this process, under the GIL, so it
        # is kept cheap: at the default interval it costs about 1% of a core on a busy node
        tree = _process_tree(self.process)
        self.memory_samples.append(_aggregate_rss_bytes(self.process, tree) / (1024**3))
        cpu_seconds, wall = _aggregate_cpu_seconds(self.process, tree), time.monotonic()
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
