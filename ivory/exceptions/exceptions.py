class IllegalAccessException(Exception):
    """Raised when an immutable struct is tried to be modified"""
    pass


class NotImplementedException(Exception):
    """Raised when a methods of an ABC are not overwritten"""
    pass


class InvalidAttributeException(Exception):
    """Raised when attributes are not valid"""
    pass


class UnsupportedPluginTypeException(Exception):
    """Raised when a plugin cannot be found or be instanciated"""
    pass


class InvalidLoopException(Exception):
    """Raised when a loop cannot be executed properly"""
    pass
