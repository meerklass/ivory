from ivory.utils.classproperty import classproperty


class ConfigSection(dict):
    """Class to represent the config file sections."""

    @classproperty
    def name(cls):
        return cls.__name__
