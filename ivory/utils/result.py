from enum import Enum
from typing import NamedTuple, Any


class Result(NamedTuple):
    """
    A `NamedTuple` containing `location`, the key for storage in the context, `result`, the actual result and
    `allow_overwrite`, which disables overwriting of the result once stored in the context.
    """
    location: Enum
    result: Any
    allow_overwrite: bool = True
