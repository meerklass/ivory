import importlib
import importlib.util
import os
import pickle
import sys
import uuid
from enum import Enum
from getopt import getopt
from pathlib import Path
from types import ModuleType
from typing import Any

from ivory import context
from ivory.backend import SequentialBackend
from ivory.config_keys import ConfigKeys
from ivory.context import ctx
from ivory.exceptions.exceptions import InvalidAttributeException
from ivory.loop import Loop
from ivory.utils.config_section import ConfigSection
from ivory.utils.infer_type import InferType
from ivory.utils.opt_helper import get_all_longopts, get_opt_parameter_dict
from ivory.utils.struct import ImmutableStruct, Struct


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
        """Get ready for `launch`."""
        config = self._parse_args(argv=argv)

        if ConfigKeys.PIPELINE.value not in config:
            raise ValueError('The loaded config must contain a section "Pipeline".')

        if ConfigKeys.PLUGINS.value not in config.Pipeline:
            raise InvalidAttributeException("plugins definition is missing")

        ctx().params = context.create_immutable_ctx(**config)
        ctx().plugins = ctx().params.Pipeline.plugins

        # Load context if provided (defaults to None if not specified, allowing CLI override)
        context_file = config[ConfigKeys.PIPELINE.value].get(
            ConfigKeys.CONTEXT.value, None
        )
        if context_file is not None:
            with open(context_file, "rb") as input_file:
                context_from_disc = pickle.load(input_file)
            self._load_context_into_ctx(context_=context_from_disc)

    def _parse_args(self, argv: list[str]) -> ImmutableStruct:
        """Parse the command line input `argv` and create and return an immutable context from it."""
        if argv is None or len(argv) < 1:
            raise ValueError(
                f"Input `argv` must not be empty `list` or `None`, got {argv}."
            )
        config_sections = self._get_config_sections(config_name=argv[-1])

        # overwrite parameters by command line options
        all_longopts = get_all_longopts(config_sections=config_sections)
        opt_list, positional = getopt(argv, "", all_longopts)
        if (positional_len := len(positional)) != 1:
            raise InvalidAttributeException(
                f"There must be exactly one config file given, got {positional_len}."
            )
        return self._config_immutable(
            config_sections, get_opt_parameter_dict(opt_list=opt_list)
        )

    @staticmethod
    def _config_immutable(
        config_sections: dict[str, ConfigSection],
        opt_parameter_dict: dict[str, ConfigSection] | None = None,
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
                if (
                    section_name_is_in_opts
                    and config_key in opt_parameter_dict[section_name]
                ):
                    opt_value = opt_parameter_dict[section_name][config_key]
                    config_value = InferType.infer_type(opt_value, config_value)
                if (
                    section_name == ConfigKeys.PIPELINE.value
                    and config_key == ConfigKeys.PLUGINS.value
                    and isinstance(config_value, list)
                ):
                    config_value = Loop(config_value)
                section_dict[config_key] = config_value
            if len(section_dict) > 0:  # otherwise no entries were inside
                attribute_dict[section_name] = context.create_immutable_ctx(
                    **section_dict
                )
        return context.create_immutable_ctx(**attribute_dict)

    def _get_config_sections(self, config_name: str) -> dict[str, ConfigSection]:
        """Returns a potentially empty `dict` of config section names and `ConfigSection`s."""
        result = {}
        config = self._load_config(config_name)
        for section_name in dir(config):
            if config_section := self._get_config_section(config, section_name):
                result[section_name] = config_section

        # Ensure Pipeline always has context key to allow CLI override
        if (
            ConfigKeys.PIPELINE.value in result
            and ConfigKeys.CONTEXT.value not in result[ConfigKeys.PIPELINE.value]
        ):
            result[ConfigKeys.PIPELINE.value][ConfigKeys.CONTEXT.value] = None

        return result

    @staticmethod
    def _load_config(config_name: str) -> ModuleType:
        """
        Load a config either as a dotted module name (e.g. 'museek.config.demo') or as a
        filesystem path to a `.py` file (absolute, relative, or `~`-expanded), which does not
        need to be part of an installed/importable package.
        """
        path_separators = (sep for sep in (os.sep, os.altsep) if sep)
        looks_like_path = any(
            sep in config_name for sep in path_separators
        ) or config_name.endswith(".py")
        if looks_like_path:
            config_path = Path(config_name).expanduser().resolve()
            if not config_path.is_file():
                raise FileNotFoundError(f"Configuration file not found: {config_path}")
            module_name = f"ivory_dynamic_config_{uuid.uuid4().hex}"
            spec = importlib.util.spec_from_file_location(module_name, config_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load configuration from {config_path}")
            config = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = config
            spec.loader.exec_module(config)
            return config
        return importlib.import_module(config_name)

    @staticmethod
    def _get_config_section(config: ModuleType, section_name: str) -> Any | None:
        """
        Returns the attribute `section_name` in `config`
        if `section_name` belongs to a valid configuration file section
        and if the attribute is of `ConfigSection` type.
        """
        if (
            not section_name.startswith("__")
            and section_name[0].upper() == section_name[0]
            and section_name != ConfigSection.name
            and isinstance(
                config_section := getattr(config, section_name), ConfigSection
            )
        ):
            return config_section

    @staticmethod
    def _load_context_into_ctx(context_: Struct):
        """Load results into ctx(). Results are identified by having `Enum`s as keys."""
        for key_, value_ in context_.items():
            if isinstance(key_, Enum):
                ctx()[key_] = value_
