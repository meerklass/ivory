from collections import abc
from enum import Enum

from ivy.exceptions.exceptions import IllegalAccessException


class WorkflowState(Enum):
    RUN = 'RUN'
    STOP = 'STOP'
    EXIT = 'EXIT'
    RESUME = 'RESUME'


class ImmutableStruct(abc.MutableMapping):
    """
    A `dict`-like object, whose keys can be accessed with the usual
    '[...]' lookup syntax, or with the '.' get attribute syntax.

    Examples::

      >>> a = Struct()
      >>> a['x'] = 1
      >>> a.x
      1
      >>> a.y = 2
      >>> a['y']
      2

    Values can also be initially set by specifying them as keyword
    arguments to the constructor::

      >>> a = Struct(z=3)
      >>> a['z']
      3
      >>> a.z
      3

    Like `dict` instances, `Struct`s have a `copy` method to get a
    shallow copy of the instance:

      >>> b = a.copy()
      >>> b.z
      3

    """

    def __init__(self, initializer=None, **extra_args):
        if initializer is not None:
            try:
                # initializer is `dict`-like?
                for key, value in initializer.items():
                    self.__dict__[key] = value
            except AttributeError:
                # initializer is a sequence of (name,value) pairs?
                for key, value in initializer:
                    self.__dict__[key] = value
        for key, value in extra_args.items():
            self.__dict__[key] = value

    def __setitem__(self, key, value):
        raise IllegalAccessException("Trying to modify immutable struct with: %s=%s" % (str(key), str(value)))

    def __delitem__(self, key):
        raise IllegalAccessException(f'Trying to delete item "{key}" of immutable struct.')

    def __delattr__(self, key):
        raise IllegalAccessException(f'Trying to delete attribute "{key}" of immutable struct.')

    def __setattr__(self, key, value):
        raise IllegalAccessException(f'Trying to modify immutable struct {key}={value}.')

    def __getitem__(self, key):
        return self.__dict__[key]

    def __len__(self):
        return len(self.__dict__)

    def __iter__(self):
        for i in self.__dict__:
            yield i

    def __str__(self):
        """ Returns a nicely formatted `str` of `self`. """
        str = '{\n'
        for key, value in self.items():
            str += f'{key}={value}\n'
        str += '}'
        return str

    def copy(self):
        """Return a (shallow) copy of this `Struct` instance."""
        return ImmutableStruct(self)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()


class Struct(ImmutableStruct):
    """
    Mutable implementation of a Struct
    """

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __delitem__(self, key):
        del self.__dict__[key]

    def __setattr__(self, key, value):
        self.__setitem__(key=key, value=value)

    def __delattr__(self, key):
        self.__delitem__(key=key)

    def copy(self):
        """Return a (shallow) copy of this `Struct` instance."""
        return Struct(self)


class WorkflowStruct(Struct):
    """
    Struct representing the internal state of a workflow loop
    """

    iter = 0

    state = WorkflowState.RUN

    def increment(self):
        self.iter += 1

    def reset(self):
        self.iter = 0
        self.state = WorkflowState.RUN

    def stop(self):
        self.state = WorkflowState.STOP

    def exit(self):
        self.state = WorkflowState.EXIT

    def resume(self):
        self.state = WorkflowState.RESUME
