import pytest

from ivory.context import loop_ctx
from ivory.exceptions.exceptions import InvalidAttributeException
from ivory.loop import Loop
from ivory.utils.stop_criteria import RangeStopCriteria


class TestStopCriteria:
    def test_range_stop_criteria(self):
        try:
            RangeStopCriteria(0)
            pytest.fail("0 iterations not allowed")
        except InvalidAttributeException:
            assert True

        stop_criteria = RangeStopCriteria(1)
        loop = Loop("", stop_criteria)
        assert not stop_criteria.is_stop()

        loop_ctx(loop).increment()
        assert stop_criteria.is_stop()
