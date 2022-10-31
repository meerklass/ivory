import pytest

from ivy.exceptions.exceptions import IllegalAccessException
from ivy.utils.struct import ImmutableStruct
from ivy.utils.struct import Struct


class TestStruct:

    def test_struct(self):

        a = Struct()
        a['x'] = 1
        assert a.x == 1

        a.y = 2
        assert a['y'] == 2

    def test_init(self):
        a = Struct(z=3)
        assert a['z'] == 3
        assert a.z == 3

    def test_copy(self):
        a = Struct(z=3)
        b = a.copy()
        assert b.z == 3

    def test_immutable_struct_when_setitem(self):
        a = ImmutableStruct()
        try:
            a['x'] = 1
            pytest.fail("Not mutation allowed on immutable", False)
        except IllegalAccessException:
            assert True

    def test_immutable_struct_when_setattr(self):
        a = ImmutableStruct()
        try:
            a.x = 1
            pytest.fail("Not mutation allowed on immutable", False)
        except IllegalAccessException:
            assert True

    def test_immutable_struct_when_delattr(self):
        a = ImmutableStruct({'x': 1})
        try:
            del a.x
            pytest.fail("Not mutation allowed on immutable", False)
        except IllegalAccessException:
            assert True

    def test_immutable_struct_when_delitem(self):
        a = ImmutableStruct({'x': 1})
        try:
            del a['x']
            pytest.fail("Not mutation allowed on immutable", False)
        except IllegalAccessException:
            assert True
