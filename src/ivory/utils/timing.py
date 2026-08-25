from collections import OrderedDict


class SimpleTiming:
    """
    classdocs
    """

    def __init__(self, name, duration):
        self.name = name
        self.duration = duration

    def __str__(self):
        return f"{self.name!s:30}: {self.duration:>7.0f} s"


class ResourceTiming(SimpleTiming):
    """
    Timing information with resource usage metrics (memory and CPU).
    Tracks both average and peak values.
    """

    def __init__(
        self,
        name,
        duration,
        peak_memory_gb=0.0,
        peak_cpu_percent=0.0,
        avg_memory_gb=0.0,
        avg_cpu_percent=0.0,
    ):
        super().__init__(name, duration)
        self.peak_memory_gb = peak_memory_gb
        self.peak_cpu_percent = peak_cpu_percent
        self.avg_memory_gb = avg_memory_gb if avg_memory_gb > 0 else peak_memory_gb
        self.avg_cpu_percent = (
            avg_cpu_percent if avg_cpu_percent > 0 else peak_cpu_percent
        )

    def __str__(self):
        return (
            f"{self.name!s:30}: {self.duration:>7.0f} s | "
            f"Mem(Avg/Peak): {self.avg_memory_gb:>6.2f}/{self.peak_memory_gb:>6.2f} GB | "
            f"CPU(Avg/Peak): {self.avg_cpu_percent:>5.1f}/{self.peak_cpu_percent:>5.1f}%"
        )


class TimingCollection(SimpleTiming):
    def __init__(self, parent):
        super().__init__(parent, 0)
        self.timings = OrderedDict()

    def add_timing(self, timing):
        try:
            self.timings[timing.name].append(timing.duration)
        except KeyError:
            self.timings[timing.name] = [timing.duration]

    def __str__(self):
        s = ""
        for name, durations in self.timings.items():
            s += f"   {name!s:30}({len(durations)}): mean:{sum(durations) / len(durations):>7.3f}s sum:{sum(durations):>7.3f}s min:{min(durations):>7.3f}s max:{max(durations):>7.3f}s\n"

        return s


class ResourceTimingCollection(SimpleTiming):
    """
    Collection of ResourceTiming objects for aggregating statistics across multiple runs.
    """

    def __init__(self, parent):
        super().__init__(parent, 0)
        self.timings = OrderedDict()

    def add_timing(self, timing):
        if not isinstance(timing, ResourceTiming):
            raise TypeError(f"Expected ResourceTiming, got {type(timing)}")
        try:
            self.timings[timing.name].append(timing)
        except KeyError:
            self.timings[timing.name] = [timing]

    def __str__(self):
        s = ""
        for name, timings_list in self.timings.items():
            durations = [t.duration for t in timings_list]
            avg_memories = [t.avg_memory_gb for t in timings_list]
            peak_memories = [t.peak_memory_gb for t in timings_list]
            avg_cpus = [t.avg_cpu_percent for t in timings_list]
            peak_cpus = [t.peak_cpu_percent for t in timings_list]
            s += (
                f"   {name!s:30}({len(timings_list)}): "
                f"Time - mean:{sum(durations) / len(durations):>7.3f}s sum:{sum(durations):>7.3f}s | "
                f"Mem(Avg/Peak) - mean:{sum(avg_memories) / len(avg_memories):>6.2f}/{sum(peak_memories) / len(peak_memories):>6.2f}GB max:{max(peak_memories):>6.2f}GB | "
                f"CPU(Avg/Peak) - mean:{sum(avg_cpus) / len(avg_cpus):>5.1f}/{sum(peak_cpus) / len(peak_cpus):>5.1f}% max:{max(peak_cpus):>5.1f}%\n"
            )
        return s
