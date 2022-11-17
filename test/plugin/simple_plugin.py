from ivory.plugin.abstract_plugin import AbstractPlugin


class SimplePlugin(AbstractPlugin):
    """
    Simple implementation of the AbstractPlugin
    """

    def run(self):
        if 'value' in self.config:
            print(self.config.value)

    def set_requirements(self):
        pass
