import unittest
from unittest.mock import MagicMock, Mock, call, patch

from ivory.enum.context_storage_enum import ContextStorageEnum
from ivory.utils.loop_runner import LoopRunner
from ivory.utils.requirement import Requirement
from ivory.utils.result import Result
from ivory.utils.struct import Struct


class TestLoopRunner(unittest.TestCase):
    def setUp(self):
        mock_loop = MagicMock()
        self.loop_runner = LoopRunner(loop=mock_loop)

    @patch.object(LoopRunner, "_store_ctx")
    @patch.object(LoopRunner, "_print_timings")
    def test_call(self, mock_print_timings, mock_store_ctx):
        mock_plugin_1 = MagicMock(results=[Result(result="a", location="a")])
        mock_plugin_2 = MagicMock(results=[Result(result="b", location="b")])
        self.loop_runner.loop.__iter__ = MagicMock(return_value=iter([mock_plugin_1, mock_plugin_2]))
        context = Struct({"timings": []})
        result_context = self.loop_runner(ctx=context)
        self.assertEqual(2, mock_store_ctx.call_count)
        self.assertTrue(result_context.timings)
        self.assertEqual("a", result_context["a"].result)
        self.assertEqual("b", result_context["b"].result)
        self.loop_runner.loop.reset.assert_called_once()
        mock_print_timings.assert_called_once()

    def test_store_to_ctx(self):
        context = Struct()
        mock_results = [Result(result="a", location="a")]
        self.loop_runner._store_to_ctx(results=mock_results, ctx=context)
        self.assertEqual("a", context["a"].result)

    def test_store_to_ctx_when_overwrite_disabled_expect_result_unchanged(self):
        context = Struct({"a": Result(result="b", location="a", allow_overwrite=False)})
        mock_results = [Result(result="a", location="a")]
        self.loop_runner._store_to_ctx(results=mock_results, ctx=context)
        self.assertEqual("b", context["a"].result)

    def test_store_to_ctx_when_overwrite_enabled_expect_result_changed(self):
        context = Struct({"a": Result(result="b", location="a", allow_overwrite=True)})
        mock_results = [Result(result="a", location="a")]
        self.loop_runner._store_to_ctx(results=mock_results, ctx=context)
        self.assertEqual("a", context["a"].result)

    @patch("ivory.utils.loop_runner.pickle")
    @patch("ivory.utils.loop_runner.open")
    @patch("ivory.utils.loop_runner.os")
    def test_store_ctx(self, mock_os, mock_open, mock_pickle):
        mock_directory = Mock()
        mock_file_name = Mock()
        context = Struct(
            {
                ContextStorageEnum.DIRECTORY: mock_directory,
                ContextStorageEnum.FILE_NAME: mock_file_name,
            }
        )
        self.assertIsNone(LoopRunner._store_ctx(ctx=context))
        mock_os.path.join.assert_called_once_with(mock_directory.result, mock_file_name.result)
        mock_open.assert_called_once_with(mock_os.path.join.return_value, "wb")
        mock_pickle.dump.assert_called_once_with(
            Struct({ContextStorageEnum.DIRECTORY: None, ContextStorageEnum.FILE_NAME: None}),
            mock_open().__enter__(),
        )

    @patch("ivory.utils.loop_runner.os")
    def test_store_ctx_when_key_error_expect_nothing_done(self, mock_os):
        context = Struct()
        self.assertIsNone(LoopRunner._store_ctx(ctx=context))
        mock_os.path.join.assert_not_called()

    @patch("ivory.utils.loop_runner.os")
    def test_store_ctx_when_storage_directories_none_expect_nothing_done(self, mock_os):
        context = Struct({ContextStorageEnum.DIRECTORY: None, ContextStorageEnum.FILE_NAME: None})
        self.assertIsNone(LoopRunner._store_ctx(ctx=context))
        mock_os.path.join.assert_not_called()

    def test_run_args(self):
        mock_plugin = MagicMock()
        mock_plugin.requirements = [Requirement(location="a", variable="a")]
        context = Struct({"a": Result(result="value", location="a")})
        arguments = self.loop_runner._run_args(plugin=mock_plugin, ctx=context)
        self.assertEqual("value", arguments["a"])
        self.assertEqual(1, len(arguments.keys()))

    @patch("ivory.utils.loop_runner.print")
    def test_print_timings(self, mock_print):
        mock_timing = MagicMock()
        self.loop_runner._print_timings(timings_list=[mock_timing])
        expected_calls = [call("\n--> Timings:", flush=True), call(mock_timing)]
        mock_print.assert_has_calls(calls=expected_calls)
