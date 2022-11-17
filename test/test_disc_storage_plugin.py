import os
import unittest

from ivory.enum.plugin_enum import PluginEnum
from ivory.plugin.disc_storage_plugin import DiscStoragePlugin
from ivory.utils.requirement import Requirement
from ivory.utils.struct import Struct


class TestDiscStoragePlugin(unittest.TestCase):
    def setUp(self):
        self.cache_dir = './cache/'
        self.file_name = 'test_context.pickle'
        os.makedirs(self.cache_dir, exist_ok=True)

    def test_set_requirements(self):
        disc_storage_plugin = DiscStoragePlugin(ctx=Struct())
        self.assertListEqual(
            [Requirement(location=PluginEnum.CONTEXT_STORAGE_DIRECTORY, variable='storage_directory'),
             Requirement(location=PluginEnum.CONTEXT_FILE_NAME, variable='file_name')],
            disc_storage_plugin.requirements
        )

    def test_run(self):
        disc_storage_plugin = DiscStoragePlugin(ctx=Struct({'a': 1}))
        disc_storage_plugin.run(storage_directory=self.cache_dir, file_name=self.file_name)
        self.assertTrue(os.path.exists(os.path.join(self.cache_dir, self.file_name)))

    def tearDown(self):
        if os.path.exists(to_delete := os.path.join(self.cache_dir, self.file_name)):
            os.remove(to_delete)
        os.rmdir(self.cache_dir)
