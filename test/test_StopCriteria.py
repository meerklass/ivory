# IVY is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# IVY is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with IVY.  If not, see <http://www.gnu.org/licenses/>.


"""
Tests for `ivy.stop_criteria` module.

author: jakeret
"""

import pytest

from ivy.context import loop_ctx
from ivy.exceptions.exceptions import InvalidAttributeException
from ivy.loop import Loop
from ivy.utils.stop_criteria import RangeStopCriteria


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
