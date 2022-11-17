from enum import Enum
from typing import NamedTuple


class Requirement(NamedTuple):
    """
    A `NamedTuple` containing `location`, a requirement's key for lookup in the context,
    and `variable`, the name of the argument in the plugin run method.
    """
    location: Enum | str
    variable: str
