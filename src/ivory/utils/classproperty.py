class classproperty:
    """Descriptor combining classmethod and property semantics.

    Works when accessed on the class itself (``Cls.attr``) or on an
    instance (``instance.attr``), always passing the owning class to
    the wrapped function.
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, owner=None):
        if owner is None:
            owner = type(obj)
        return self.func(owner)
