import unittest
from unittest.mock import patch, MagicMock

from ivory.backend import SequentialBackend
from ivory.utils.struct import Struct


class TestSequentialBackend(unittest.TestCase):
    @patch('ivory.backend.LoopRunner')
    def test_run(self, mock_loop_runner):
        mock_loop = MagicMock()
        sequential_backend = SequentialBackend(ctx=Struct())
        sequential_backend.run(loop=mock_loop)
        mock_loop_runner.assert_called_once_with(mock_loop)
        mock_loop_runner().assert_called_once_with(Struct())


if __name__ == '__main__':
    unittest.main()
