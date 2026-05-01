from collections import OrderedDict


class SimpleTiming:
    """
    classdocs
    """

    def __init__(self, name, duration):
        self.name = name
        self.duration = duration

    def __str__(self):
        return "{0!s:30}: {1:>7.0f} s".format(self.name, self.duration)


class ResourceTiming(SimpleTiming):
    """
    Timing information with resource usage metrics (memory and CPU).
    """

    def __init__(self, name, duration, peak_memory_gb=0.0, peak_cpu_percent=0.0):
        super().__init__(name, duration)
        self.peak_memory_gb = peak_memory_gb
        self.peak_cpu_percent = peak_cpu_percent

    def __str__(self):
        return (
            "{0!s:30}: {1:>7.0f} s | Memory: {2:>7.2f} GB | CPU: {3:>6.1f}%"
            .format(self.name, self.duration, self.peak_memory_gb, self.peak_cpu_percent)
        )


class TimingCollection(SimpleTiming):

    def __init__(self, parent):
        super(TimingCollection, self).__init__(parent, 0)
        self.timings = OrderedDict()

    def add_timing(self, timing):
        try:
            self.timings[timing.name].append(timing.duration)
        except KeyError:
            self.timings[timing.name] = [timing.duration]

    def __str__(self):
        s = ""
        for name, durations in self.timings.items():
            s += "   {0!s:30}({1}): mean:{2:>7.3f}s sum:{3:>7.3f}s min:{4:>7.3f}s max:{5:>7.3f}s\n".format(
                name,
                len(durations),
                sum(durations) / len(durations),
                sum(durations),
                min(durations),
                max(durations)
            )

        return s


class ResourceTimingCollection(SimpleTiming):
    """
    Collection of ResourceTiming objects for aggregating statistics across multiple runs.
    """

    def __init__(self, parent):
        super(ResourceTimingCollection, self).__init__(parent, 0)
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
            memories = [t.peak_memory_gb for t in timings_list]
            cpus = [t.peak_cpu_percent for t in timings_list]
            s += (
                "   {0!s:30}({1}): "
                "Time - mean:{2:>7.3f}s sum:{3:>7.3f}s | "
                "Memory - mean:{4:>7.2f}GB max:{5:>7.2f}GB | "
                "CPU - mean:{6:>6.1f}% max:{7:>6.1f}%\n"
                .format(
                    name,
                    len(timings_list),
                    sum(durations) / len(durations),
                    sum(durations),
                    sum(memories) / len(memories),
                    max(memories),
                    sum(cpus) / len(cpus),
                    max(cpus)
                )
            )
        return s
