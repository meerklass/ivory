class ConfigSection(dict):
    """Class to represent the config file sections."""

    @classmethod
    @property
    def name(self):
        return self.__name__
