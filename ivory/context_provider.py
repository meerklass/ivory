from ivory.utils.struct import ImmutableStruct, Struct


class DefaultContextProvider:
    """
    Default implementation of a context provider.
    Creates a simple mutable struct as ctx and doesn't
    persist the context.
    """

    @staticmethod
    def create_context(**args):
        """
        Returns a Struct
        """
        return Struct(**args)

    @staticmethod
    def create_immutable_context(**args):
        """
        Returns a Struct
        """
        return ImmutableStruct(**args)

    @staticmethod
    def store_context():
        """
        Dummy method. Nothing is stored
        """
        pass
