import os
import pickle

from ivory.enum.plugin_enum import PluginEnum
from ivory.plugin.abstract_plugin import AbstractPlugin
from ivory.utils.requirement import Requirement
from ivory.utils.struct import Struct


class DiscStoragePlugin(AbstractPlugin):
    """ Stores the context `ctx` to hard disc. """

    def __init__(self, ctx: Struct):
        """ Initializes with context `ctx`. """
        super().__init__(ctx=ctx)
        self.ctx = ctx

    def run(self, storage_directory: str, file_name: str):
        """
        Run the plugin.
        :param storage_directory: directory to store the pickled context
        :param file_name: name of the pickle file
        """
        output_file = os.path.join(storage_directory, file_name)
        with open(output_file, "wb") as context_file:
            pickle.dump(self.ctx, context_file)

    def set_requirements(self):
        self.requirements = [Requirement(location=PluginEnum.CONTEXT_STORAGE_DIRECTORY,
                                         variable='storage_directory'),
                             Requirement(location=PluginEnum.CONTEXT_FILE_NAME,
                                         variable='file_name')]
