import pytest

from ivory.utils.timing import (
    ResourceTiming,
    ResourceTimingCollection,
    SimpleTiming,
    TimingCollection,
)


class TestSimpleTiming:
    def test_str(self):
        timing = SimpleTiming("MyPlugin", 12.3)
        assert "MyPlugin" in str(timing)
        assert "12" in str(timing)


class TestResourceTiming:
    def test_str_contains_name_and_metrics(self):
        timing = ResourceTiming(
            "MyPlugin",
            5.0,
            peak_memory_gb=2.0,
            peak_cpu_percent=50.0,
            avg_memory_gb=1.0,
            avg_cpu_percent=25.0,
        )
        s = str(timing)
        assert "MyPlugin" in s
        assert "1.00" in s
        assert "2.00" in s

    def test_avg_memory_falls_back_to_peak_when_zero(self):
        """`timing.py:35` deliberately treats `avg_memory_gb <= 0` (i.e. no samples were
        ever collected) as "use the peak instead" rather than reporting a bare zero."""
        timing = ResourceTiming("MyPlugin", 1.0, peak_memory_gb=3.5, avg_memory_gb=0.0)
        assert timing.avg_memory_gb == 3.5

    def test_avg_memory_kept_when_positive(self):
        timing = ResourceTiming("MyPlugin", 1.0, peak_memory_gb=3.5, avg_memory_gb=1.2)
        assert timing.avg_memory_gb == 1.2

    def test_avg_cpu_falls_back_to_peak_when_zero(self):
        timing = ResourceTiming(
            "MyPlugin", 1.0, peak_cpu_percent=80.0, avg_cpu_percent=0.0
        )
        assert timing.avg_cpu_percent == 80.0

    def test_avg_cpu_kept_when_positive(self):
        timing = ResourceTiming(
            "MyPlugin", 1.0, peak_cpu_percent=80.0, avg_cpu_percent=10.0
        )
        assert timing.avg_cpu_percent == 10.0

    def test_defaults_are_zero(self):
        timing = ResourceTiming("MyPlugin", 1.0)
        assert timing.peak_memory_gb == 0.0
        assert timing.avg_memory_gb == 0.0
        assert timing.peak_cpu_percent == 0.0
        assert timing.avg_cpu_percent == 0.0


class TestTimingCollection:
    def test_add_timing_groups_by_name(self):
        collection = TimingCollection("MyLoop")
        collection.add_timing(SimpleTiming("PluginA", 1.0))
        collection.add_timing(SimpleTiming("PluginA", 3.0))
        collection.add_timing(SimpleTiming("PluginB", 2.0))

        assert collection.timings["PluginA"] == [1.0, 3.0]
        assert collection.timings["PluginB"] == [2.0]

    def test_str_reports_mean_sum_min_max(self):
        collection = TimingCollection("MyLoop")
        collection.add_timing(SimpleTiming("PluginA", 1.0))
        collection.add_timing(SimpleTiming("PluginA", 3.0))
        s = str(collection)
        assert "PluginA" in s
        assert "mean" in s
        assert "sum" in s


class TestResourceTimingCollection:
    def test_add_timing_rejects_non_resource_timing(self):
        collection = ResourceTimingCollection("MyLoop")
        with pytest.raises(TypeError):
            collection.add_timing(SimpleTiming("PluginA", 1.0))

    def test_add_timing_groups_by_name(self):
        collection = ResourceTimingCollection("MyLoop")
        t1 = ResourceTiming(
            "PluginA",
            1.0,
            peak_memory_gb=1.0,
            avg_memory_gb=0.5,
            peak_cpu_percent=10.0,
            avg_cpu_percent=5.0,
        )
        t2 = ResourceTiming(
            "PluginA",
            2.0,
            peak_memory_gb=2.0,
            avg_memory_gb=1.5,
            peak_cpu_percent=20.0,
            avg_cpu_percent=15.0,
        )
        collection.add_timing(t1)
        collection.add_timing(t2)
        assert collection.timings["PluginA"] == [t1, t2]

    def test_str_reports_aggregated_metrics(self):
        collection = ResourceTimingCollection("MyLoop")
        collection.add_timing(
            ResourceTiming(
                "PluginA",
                1.0,
                peak_memory_gb=1.0,
                avg_memory_gb=0.5,
                peak_cpu_percent=10.0,
                avg_cpu_percent=5.0,
            )
        )
        s = str(collection)
        assert "PluginA" in s
        assert "Mem(Avg/Peak)" in s
        assert "CPU(Avg/Peak)" in s


if __name__ == "__main__":
    pytest.main()
