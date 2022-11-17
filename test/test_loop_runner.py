import unittest
from unittest.mock import MagicMock, patch, call

from ivory.utils.loop_runner import LoopRunner
from ivory.utils.requirement import Requirement
from ivory.utils.result import Result
from ivory.utils.struct import Struct


class TestLoopRunner(unittest.TestCase):
    def setUp(self):
        mock_loop = MagicMock()
        self.loop_runner = LoopRunner(loop=mock_loop)

    @patch.object(LoopRunner, '_print_timings')
    def test_call(self, mock_print_timings):
        mock_plugin_1 = MagicMock(results=[Result(result='a', location='a')])
        mock_plugin_2 = MagicMock(results=[Result(result='b', location='b')])
        self.loop_runner.loop.__iter__ = MagicMock(return_value=iter([mock_plugin_1, mock_plugin_2]))
        context = Struct({'timings': []})
        result_context = self.loop_runner(ctx=context)
        self.assertTrue(result_context.timings)
        self.assertEqual('a', result_context['a'].result)
        self.assertEqual('b', result_context['b'].result)
        self.loop_runner.loop.reset.assert_called_once()
        mock_print_timings.assert_called_once()

    def test_store_to_ctx(self):
        context = Struct()
        mock_results = [Result(result='a', location='a')]
        self.loop_runner._store_to_ctx(results=mock_results, ctx=context)
        self.assertEqual('a', context['a'].result)

    def test_store_to_ctx_when_overwrite_disabled_expect_result_unchanged(self):
        context = Struct({'a': Result(result='b', location='a', allow_overwrite=False)})
        mock_results = [Result(result='a', location='a')]
        self.loop_runner._store_to_ctx(results=mock_results, ctx=context)
        self.assertEqual('b', context['a'].result)

    def test_store_to_ctx_when_overwrite_enabled_expect_result_changed(self):
        context = Struct({'a': Result(result='b', location='a', allow_overwrite=True)})
        mock_results = [Result(result='a', location='a')]
        self.loop_runner._store_to_ctx(results=mock_results, ctx=context)
        self.assertEqual('a', context['a'].result)

    def test_run_args(self):
        mock_plugin = MagicMock()
        mock_plugin.requirements = [Requirement(location='a', variable='a')]
        context = Struct({'a': Result(result='value', location='a')})
        arguments = self.loop_runner._run_args(plugin=mock_plugin, ctx=context)
        self.assertEqual('value', arguments['a'])
        self.assertEqual(1, len(arguments.keys()))

    @patch('ivory.utils.loop_runner.print')
    def test_print_timings(self, mock_print):
        mock_timing = MagicMock()
        self.loop_runner._print_timings(timings_list=[mock_timing])
        mock_print.assert_has_calls(calls=[call('\n--> Timings:'), call(mock_timing)])
