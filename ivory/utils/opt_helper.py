from ivory.exceptions.exceptions import InvalidAttributeException
from ivory.utils.config_section import ConfigSection


def get_all_longopts(config_sections: dict[str, ConfigSection]) -> list[str]:
    """Returns all parameter names in `config_sections` as a list of command-line argument longopts strings."""
    result = []
    for section_name, section_dict in config_sections.items():
        for parameter_name in section_dict:
            result.append(f"{section_name}-{parameter_name.replace('_', '-')}=")
    return result


def get_section_parameter_name_from_opt(opt: tuple[str]) -> tuple[str, str, str]:
    """
    Splits the opt into section name, parameter name and parameter value, all as `str`.
    Replaces '-' with '_'.
    Example: `('--ExamplePlugin-example-parameter', '2')` becomes `('ExamplePlugin', 'example_parameter', '2')`
    """
    opt_string, parameter_value = opt
    if opt_string[:2] != "--":
        raise InvalidAttributeException(f"invalid option name: {opt_string[0]}")
    list_of_parts = opt_string[2:].split("-")
    parameter_name = list_of_parts[1]
    for part in list_of_parts[2:]:
        parameter_name += "_" + part
    return list_of_parts[0], parameter_name, parameter_value


def get_opt_parameter_dict(opt_list: list[tuple[str, str]]) -> dict[str, ConfigSection]:
    """
    Returns the `opt_list` as a `dict` of section names and `ConfigSections`.
    Note: all types are `str`.
    """
    opt_parameter_dict = {}
    for opt in opt_list:
        section_name, parameter_name, parameter_value = get_section_parameter_name_from_opt(opt=opt)
        if section_name not in opt_parameter_dict:
            opt_parameter_dict[section_name] = ConfigSection()
        opt_parameter_dict[section_name][parameter_name] = parameter_value
    return opt_parameter_dict
