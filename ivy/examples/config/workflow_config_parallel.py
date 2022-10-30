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

author: jakeret
"""
from ivy.plugin.parallel_plugin_collection import ParallelPluginCollection

backend = "sequential"
cpu_count = 1
valuesMin = 1
valuesMax = 16

plugins = ParallelPluginCollection(["ivy.test.simple_square_plugin"],
                                   "ivy.test.range_map_plugin",
                                   "ivy.test.sum_reduce_plugin")
