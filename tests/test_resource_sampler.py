import subprocess
import sys
import time
import unittest
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import psutil

from ivory.plugin.abstract_parallel_joblib_plugin import AbstractParallelJoblibPlugin
from ivory.utils.resource_sampler import (
    ResourceSampler,
    _aggregate_cpu_seconds,
    _aggregate_rss_bytes,
)


def _make_mock_process(rss_bytes: int, children: list):
    process = MagicMock()
    process.memory_info.return_value = MagicMock(rss=rss_bytes)
    process.children.return_value = children
    return process


def _make_mock_child(rss_bytes: int):
    child = MagicMock()
    child.memory_info.return_value = MagicMock(rss=rss_bytes)
    return child


def _cpu_times(user=0.0, system=0.0, children_user=0.0, children_system=0.0):
    return MagicMock(
        user=user,
        system=system,
        children_user=children_user,
        children_system=children_system,
    )


class TestAggregateCpuSeconds(unittest.TestCase):
    def test_sums_own_and_finished_children_time_of_every_live_process(self):
        process = MagicMock()
        process.cpu_times.return_value = _cpu_times(1.0, 0.5, 2.0, 0.25)
        child = MagicMock()
        child.cpu_times.return_value = _cpu_times(3.0, 1.0, 0.5, 0.0)
        process.children.return_value = [child]
        self.assertEqual(8.25, _aggregate_cpu_seconds(process))

    def test_skips_child_that_disappeared_or_is_a_zombie(self):
        process = MagicMock()
        process.cpu_times.return_value = _cpu_times(user=1.0)
        vanished, zombie = MagicMock(), MagicMock()
        vanished.cpu_times.side_effect = psutil.NoSuchProcess(pid=1)
        zombie.cpu_times.side_effect = psutil.ZombieProcess(pid=2)
        process.children.return_value = [vanished, zombie]
        self.assertEqual(1.0, _aggregate_cpu_seconds(process))

    def test_children_lookup_failure_counts_the_process_alone(self):
        process = MagicMock()
        process.cpu_times.return_value = _cpu_times(user=1.0, children_user=2.0)
        process.children.side_effect = psutil.AccessDenied(pid=1)
        self.assertEqual(3.0, _aggregate_cpu_seconds(process))


class TestAggregateRssBytes(unittest.TestCase):
    def test_sums_process_and_children(self):
        process = _make_mock_process(
            rss_bytes=100,
            children=[_make_mock_child(30), _make_mock_child(20)],
        )
        self.assertEqual(150, _aggregate_rss_bytes(process))

    def test_no_children_returns_process_only(self):
        process = _make_mock_process(rss_bytes=100, children=[])
        self.assertEqual(100, _aggregate_rss_bytes(process))

    def test_skips_child_that_disappeared(self):
        vanished_child = _make_mock_child(30)
        vanished_child.memory_info.side_effect = psutil.NoSuchProcess(pid=1234)
        process = _make_mock_process(
            rss_bytes=100,
            children=[vanished_child, _make_mock_child(20)],
        )
        self.assertEqual(120, _aggregate_rss_bytes(process))

    def test_skips_child_with_access_denied(self):
        denied_child = _make_mock_child(30)
        denied_child.memory_info.side_effect = psutil.AccessDenied(pid=1234)
        process = _make_mock_process(rss_bytes=100, children=[denied_child])
        self.assertEqual(100, _aggregate_rss_bytes(process))


class TestResourceSampler(unittest.TestCase):
    def test_one_process_tree_lookup_per_poll(self):
        """The children lookup scans the whole process table; a poll must do it once, not once
        for the memory and once for the CPU."""
        process = MagicMock()
        process.memory_info.return_value = MagicMock(rss=100)
        process.children.return_value = []
        process.cpu_times.return_value = _cpu_times(user=1.0)
        sampler = ResourceSampler(process, interval=10.0)
        sampler._sample()
        self.assertEqual(1, process.children.call_count)

    def test_samples_real_current_process(self):
        sampler = ResourceSampler(psutil.Process(), interval=0.01)
        with sampler:
            time.sleep(0.05)
        self.assertGreaterEqual(len(sampler.memory_samples), 1)
        self.assertGreater(sampler.peak_memory_gb, 0.0)
        self.assertGreaterEqual(sampler.peak_memory_gb, sampler.avg_memory_gb)

    def test_empty_samples_report_zero(self):
        sampler = ResourceSampler(psutil.Process())
        self.assertEqual(0.0, sampler.avg_memory_gb)
        self.assertEqual(0.0, sampler.peak_memory_gb)
        self.assertEqual(0.0, sampler.avg_cpu_percent)
        self.assertEqual(0.0, sampler.peak_cpu_percent)

    def test_sampler_is_reusable_across_multiple_with_blocks(self):
        """Regression test: `__enter__` must reset `_stop_event` and the sample lists,
        otherwise a second `with` block on the same sampler collects only the single
        final sample from `__exit__` and blends it with the first run's samples."""
        sampler = ResourceSampler(psutil.Process(), interval=0.01)

        with sampler:
            time.sleep(0.05)
        first_run_samples = len(sampler.memory_samples)

        with sampler:
            time.sleep(0.05)
        second_run_samples = len(sampler.memory_samples)

        self.assertGreater(first_run_samples, 1)
        self.assertGreater(second_run_samples, 1)

    def test_children_lookup_failure_does_not_kill_the_poll_thread(self):
        """Regression test: `process.children(recursive=True)` raising (as it does when a
        joblib/loky worker exits mid-poll) must not silently stop background sampling."""
        process = MagicMock()
        process.memory_info.return_value = MagicMock(rss=100)
        process.children.side_effect = psutil.NoSuchProcess(pid=1234)
        process.cpu_times.return_value = _cpu_times(user=1.0)

        sampler = ResourceSampler(process, interval=0.01)
        with sampler:
            time.sleep(0.05)

        self.assertGreater(len(sampler.memory_samples), 1)


class _SleepyJoblibPlugin(AbstractParallelJoblibPlugin):
    """Runs a couple of short-lived jobs, giving worker processes/threads
    time to be observed by a background poller in between."""

    def run_job(self, anything: Any) -> Any:
        time.sleep(0.1)
        return anything

    def map(self, **kwargs) -> Generator[Any, None, None]:
        return iter([1, 2])

    def gather_and_set_result(self, *args, **kwargs):
        pass

    def set_requirements(self):
        pass


def _run_with_children_spy(plugin: AbstractParallelJoblibPlugin) -> list[list]:
    """Runs `plugin` wrapped in a real `ResourceSampler`, recording the *new*
    children (beyond whatever was already alive before this run, e.g. a
    lingering `multiprocessing.resource_tracker`, or loky worker processes
    a previous test's `Parallel()` call left pooled for reuse) seen on each
    poll of `psutil.Process.children()`.
    """
    from joblib.externals.loky import get_reusable_executor

    # loky keeps its worker pool alive across `Parallel()` calls for reuse,
    # so an earlier test's workers could otherwise get "grandfathered" into
    # this run's baseline and hide as not-new.
    get_reusable_executor(max_workers=1).shutdown(wait=True)

    baseline_pids = {p.pid for p in psutil.Process().children(recursive=True)}
    recorded_new_children_calls: list[list] = []
    real_children = psutil.Process.children

    def spy_children(self, *args, **kwargs):
        result = real_children(self, *args, **kwargs)
        recorded_new_children_calls.append(
            [p for p in result if p.pid not in baseline_pids]
        )
        return result

    with patch.object(psutil.Process, "children", spy_children):
        sampler = ResourceSampler(psutil.Process(), interval=0.02)
        with sampler:
            plugin.run()
    return recorded_new_children_calls, sampler


class TestResourceSamplerWithJoblibBackends(unittest.TestCase):
    """Merely calling `joblib.Parallel(...)` can spawn an incidental
    `multiprocessing.resource_tracker` helper process regardless of which
    backend it dispatches work to, so "zero children, ever" isn't a safe
    assertion for the threading backend. What actually distinguishes the two
    backends is that `prefer="processes"` spawns one live worker process per
    job (`n_jobs` of them) while `prefer="threads"` never does — so these
    tests compare against `n_jobs` instead of asserting an absolute zero.
    """

    def test_processes_backend_detects_child_processes(self):
        plugin = _SleepyJoblibPlugin(n_jobs=2, verbose=0, prefer="processes")
        recorded_new_children_calls, sampler = _run_with_children_spy(plugin)
        max_new_children = max((len(c) for c in recorded_new_children_calls), default=0)
        self.assertGreaterEqual(
            max_new_children,
            2,
            "expected at least one poll to observe live loky worker processes "
            "for each of the 2 jobs",
        )
        self.assertGreater(sampler.peak_memory_gb, 0.0)
        self.assertGreaterEqual(len(sampler.memory_samples), 1)

    def test_threads_backend_does_not_spawn_worker_processes(self):
        plugin = _SleepyJoblibPlugin(n_jobs=2, verbose=0, prefer="threads")
        recorded_new_children_calls, sampler = _run_with_children_spy(plugin)
        max_new_children = max((len(c) for c in recorded_new_children_calls), default=0)
        self.assertLess(
            max_new_children,
            2,
            "threading backend should not spawn one child process per job",
        )
        self.assertGreater(sampler.peak_memory_gb, 0.0)
        self.assertGreaterEqual(len(sampler.memory_samples), 1)


def _burn_cpu(seconds: float):
    end = time.process_time() + seconds
    while time.process_time() < end:
        pass


class _BusyJoblibPlugin(_SleepyJoblibPlugin):
    """Each job keeps a core busy, so the work shows up as CPU time in whichever process runs it."""

    def run_job(self, anything: Any) -> Any:
        _burn_cpu(0.4)
        return anything


class TestCpuIncludesChildProcesses(unittest.TestCase):
    """Regression test: CPU was `process.cpu_percent()` of the main process alone, so a plugin
    doing its work in loky worker processes reported almost nothing -- the main process only
    waits for them. The work must be counted wherever it runs."""

    def assert_counts_work_outside_the_main_process(self, run):
        main = psutil.Process()
        main_before, start = main.cpu_times(), time.monotonic()
        sampler = ResourceSampler(main, interval=0.05)
        with sampler:
            run()
        main_after, elapsed = main.cpu_times(), time.monotonic() - start
        main_own = (main_after.user - main_before.user) + (
            main_after.system - main_before.system
        )
        main_own_percent = 100.0 * main_own / elapsed
        # the 0.8 s of work ran elsewhere, so the tree's CPU must clearly exceed the main
        # process's own; on a single core it is close to 100%
        self.assertGreater(sampler.avg_cpu_percent, 40.0)
        self.assertGreater(sampler.avg_cpu_percent, main_own_percent + 30.0)
        self.assertGreaterEqual(sampler.peak_cpu_percent, sampler.avg_cpu_percent * 0.5)

    def test_loky_worker_processes_are_counted(self):
        from joblib.externals.loky import get_reusable_executor

        get_reusable_executor(max_workers=1).shutdown(wait=True)
        plugin = _BusyJoblibPlugin(n_jobs=2, verbose=0, prefer="processes")
        self.assert_counts_work_outside_the_main_process(plugin.run)

    def test_a_child_that_finished_inside_the_block_is_counted(self):
        code = (
            "import time\n"
            "end = time.process_time() + 0.8\n"
            "while time.process_time() < end: pass\n"
        )
        self.assert_counts_work_outside_the_main_process(
            lambda: subprocess.run([sys.executable, "-c", code], check=True)
        )

    def test_average_is_cpu_seconds_over_wall_time(self):
        sampler = ResourceSampler(psutil.Process(), interval=0.05)
        with sampler:
            _burn_cpu(0.3)
        # the main process itself kept one core busy
        self.assertGreater(sampler.avg_cpu_percent, 50.0)
        self.assertLess(sampler.avg_cpu_percent, 150.0)
