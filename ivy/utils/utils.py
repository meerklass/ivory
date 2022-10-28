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
Created on Mar 5, 2014

author: jakeret
"""

TYPE_MAP = {
    'bool': lambda x: boolify(x),
    'int': lambda x: int(x),
    'float': lambda x: float(x),
    'str': lambda x: x,
    'unicode': lambda x: x,
    'list': lambda x: x.split(','),
    'NoneType': lambda x: inferType(x)

}


def boolify(s):
    if s == 'True' or s == 'true':
        return True
    if s == 'False' or s == 'false':
        return False
    raise ValueError('Not Boolean Value!')


def listify(s):
    if (s.count(",") <= 0):
        raise ValueError()

    x = s.split(",")
    l = []
    for e in x:
        l.append(inferType(e))
    return l


def inferType(var):
    """guesses the str representation of the variables type"""
    var = str(var)  # important if the parameters aren't strings...
    for caster in (boolify, int, float, listify):
        try:
            return caster(var)
        except ValueError:
            pass
    return var
