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
Tests for `ivy.simple_plugin` module.

author: jakeret
"""

import pytest

from ivy.context import ctx
from test.plugin.simple_plugin import SimplePlugin


class TestSimplePlugin:

    def test_simple(self):
        plugin = SimplePlugin(ctx())
        assert 'value' not in plugin.ctx

        plugin = SimplePlugin(ctx(), value=1)
        assert plugin.ctx.value == 1

        SimplePlugin(ctx(), foo=1)
        assert ctx().foo == 1


if __name__ == '__main__':
    pytest.main()
