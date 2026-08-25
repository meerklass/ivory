class IllegalAccessException(Exception):
    """Raised when an immutable struct is tried to be modified"""


class NotImplementedException(Exception):
    """Raised when a methods of an ABC are not overwritten"""


class InvalidAttributeException(Exception):
    """Raised when attributes are not valid"""


class UnsupportedPluginTypeException(Exception):
    """Raised when a plugin cannot be found or be instanciated"""


class InvalidLoopException(Exception):
    """Raised when a loop cannot be executed properly"""
