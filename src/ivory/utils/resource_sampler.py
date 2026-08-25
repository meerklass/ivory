import threading

import psutil


def _aggregate_rss_bytes(process: psutil.Process) -> float:
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


class ResourceSampler:
    """Context manager that polls memory (`process` and all its live children)
    and CPU percent on a background thread while the wrapped block runs.

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

    def _sample(self):
        self.memory_samples.append(_aggregate_rss_bytes(self.process) / (1024**3))
        try:
            self.cpu_samples.append(self.process.cpu_percent(interval=None))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    def _poll_loop(self):
        while not self._stop_event.is_set():
            self._sample()
            self._stop_event.wait(self.interval)

    def __enter__(self):
        self._stop_event.clear()
        self.memory_samples = []
        self.cpu_samples = []
        try:
            self.process.cpu_percent(interval=None)  # prime CPU sampling
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
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
        return (
            sum(self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0.0
        )

    @property
    def peak_cpu_percent(self) -> float:
        return max(self.cpu_samples) if self.cpu_samples else 0.0
