import pickle

from ivory.context import ctx
from ivory.utils.struct import ImmutableStruct
from ivory.utils.struct import Struct


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


class PickleContextProvider(DefaultContextProvider):
    """
    Extends the DefaultContextProvider. 
    Persists the context to the disk by using pickle.
    Requires the attribute 'ctx_file_name' in the ctx 
    """

    @staticmethod
    def store_context():
        """
        Writes the current ctx to the disk
        """
        file_name = ctx().ctx_file_name
        with open(file_name, "wb") as ctxFile:
            pickle.dump(ctx(), ctxFile)
