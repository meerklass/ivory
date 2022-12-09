from abc import ABC, abstractmethod

from ivory.enum.context_storage_enum import ContextStorageEnum
from ivory.utils.requirement import Requirement
from ivory.utils.result import Result


class AbstractPlugin(ABC):
    """
    Abstract base class for all plugins.
    The config for a plugin is made accessible via `self.config
    The input arguments of the `run` method need to be defined in `cls.requirements`.
    """

    requirements: list[Requirement] = []

    def __init__(self):
        """ Initialise by setting an empty list of `Result`s and setting the requirements of `self.run()`. """
        self.results: list[Result] = []
        self.set_requirements()

    def __str__(self):
        """ Returns the name of the plugin class. """
        return self.name

    @abstractmethod
    def run(self, **kwargs):
        """ Run the plugin and store results. """
        pass

    @abstractmethod
    def set_requirements(self):
        """ Set the requirements of `self`, i.e. the arguments of `self.run()`. """
        self.requirements = []

    @classmethod
    @property
    def name(self):
        """ Returns the name of `self`. """
        return self.__name__

    def set_result(self, result: Result):
        """ Appends `result` to `self.result`. """
        self.results.append(result)

    def store_context_to_disc(self, context_file_name: str, context_directory: str):
        """
        Stores the context to disc after finishing execution of `self.run()`.
        :param context_file_name: string with context file name
        :param context_directory: string with path to folder containing context file
        """
        self.set_result(Result(result=context_file_name, location=ContextStorageEnum.FILE_NAME, allow_overwrite=True))
        self.set_result(Result(result=context_directory, location=ContextStorageEnum.DIRECTORY, allow_overwrite=True))
