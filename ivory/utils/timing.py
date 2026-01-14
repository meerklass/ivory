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
