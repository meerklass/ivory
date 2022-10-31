import importlib
from getopt import getopt
from types import ModuleType
from typing import Optional, Any

from ivory import context
from ivory.backend import SequentialBackend
from ivory.config_keys import ConfigKeys
from ivory.context import ctx
from ivory.exceptions.exceptions import InvalidAttributeException
from ivory.loop import Loop
from ivory.utils.config_section import ConfigSection
from ivory.utils.infer_type import InferType
from ivory.utils.opt_helper import get_all_longopts, get_opt_parameter_dict
from ivory.utils.struct import ImmutableStruct


class WorkflowManager:
    """
    Manages the workflow process by loading the passed config and
    parsing the passed arguments and then iterating through the plugins.
    """

    def __init__(self, argv: list[str]):
        """
        :param argv: command line input
        """
        self._setup(argv=argv)

    @staticmethod
    def launch():
        """
        Launches the workflow
        """
        ctx().timings = []
        executor = SequentialBackend(ctx())
        executor.run(ctx().params.Pipeline.plugins)

    def _setup(self, argv: list[str]):
        """ Get ready for `launch`. """
        config = self._parse_args(argv=argv)

        if ConfigKeys.PIPELINE.value not in config:
            raise ValueError('The loaded config must contain a section "Pipeline".')

        if ConfigKeys.PLUGINS.value not in config.Pipeline.keys():
            raise InvalidAttributeException("plugins definition is missing")

        if ConfigKeys.CONTEXT_PROVIDER.value in config.Pipeline.keys():
            def get_context_provider_wrapper():
                class_name = config.Pipeline[ConfigKeys.CONTEXT_PROVIDER.value]
                module_name = ".".join(class_name.split(".")[:-1])
                module = importlib.import_module(module_name)
                return getattr(module, class_name.split(".")[-1])

            context.get_context_provider = get_context_provider_wrapper
        ctx().params = context.create_immutable_ctx(**config)
        ctx().plugins = ctx().params.Pipeline.plugins

    def _parse_args(self, argv: list[str]) -> ImmutableStruct:
        """ Parse the command line input `argv` and create and return an immutable context from it. """
        if argv is None or len(argv) < 1:
            raise ValueError(f'Input `argv` must not be empty `list` or `None`, got {argv}.')
        config_sections = self._get_config_sections(config_name=argv[-1])

        # overwrite parameters by command line options
        all_longopts = get_all_longopts(config_sections=config_sections)
        opt_list, positional = getopt(argv, '', all_longopts)
        if positional_len := len(positional) != 1:
            raise InvalidAttributeException(f'There must be exactly one config file given, got {positional_len}.')
        return self._config_immutable(config_sections, get_opt_parameter_dict(opt_list=opt_list))

    @staticmethod
    def _config_immutable(
            config_sections: dict[str, ConfigSection],
            opt_parameter_dict: Optional[dict[str, ConfigSection]] = None
    ) -> ImmutableStruct:
        """
        Returns an `ImmutableStruct` created from `config_section` and overwriting its entries with everything
        that is given in `opt_parameter_dict.
        :param config_sections: `dict` of section names and `ConfigSection`s
        :param opt_parameter_dict: same type as `config_sections`, coming from the command line arguments, optional
        :return: an immutable `Struct` context
        """

        attribute_dict = {}
        if opt_parameter_dict is None:
            opt_parameter_dict = {}
        for section_name, config_dict in config_sections.items():
            section_name_is_in_opts = section_name in opt_parameter_dict
            section_dict = {}
            for config_key, config_value in config_dict.items():
                # overwrite config file entry with command line input if available
                if section_name_is_in_opts and config_key in opt_parameter_dict[section_name]:
                    opt_value = opt_parameter_dict[section_name][config_key]
                    config_value = InferType.infer_type(opt_value, config_value)
                if (section_name == ConfigKeys.PIPELINE.value
                        and config_key == ConfigKeys.PLUGINS.value
                        and isinstance(config_value, list)):
                    config_value = Loop(config_value)
                section_dict[config_key] = config_value
            if len(section_dict) > 0:  # otherwise no entries were inside
                attribute_dict[section_name] = context.create_immutable_ctx(**section_dict)
        return context.create_immutable_ctx(**attribute_dict)

    def _get_config_sections(self, config_name: str) -> dict[str, ConfigSection]:
        """ Returns a potentially empty `dict` of config section names and `ConfigSection`s. """
        result = {}
        config = importlib.import_module(config_name)
        for section_name in dir(config):
            if config_section := self._get_config_section(config, section_name):
                result[section_name] = config_section
        return result

    @staticmethod
    def _get_config_section(config: ModuleType, section_name: str) -> Optional[Any]:
        """
        Returns the attribute `section_name` in `config`
        if `section_name` belongs to a valid configuration file section
        and if the attribute is of `ConfigSection` type.
        """
        if (not section_name.startswith("__")
                and section_name[0].upper() == section_name[0]
                and section_name != ConfigSection.name):
            if isinstance(config_section := getattr(config, section_name), ConfigSection):
                return config_section
