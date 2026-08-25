import time
import unittest
from typing import Any, Generator
from unittest.mock import MagicMock, patch

import psutil

from ivory.plugin.abstract_parallel_joblib_plugin import AbstractParallelJoblibPlugin
from ivory.utils.resource_sampler import ResourceSampler, _aggregate_rss_bytes


def _make_mock_process(rss_bytes: int, children: list):
    process = MagicMock()
    process.memory_info.return_value = MagicMock(rss=rss_bytes)
    process.children.return_value = children
    return process


def _make_mock_child(rss_bytes: int):
    child = MagicMock()
    child.memory_info.return_value = MagicMock(rss=rss_bytes)
    return child


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
