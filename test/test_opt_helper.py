import pytest

from ivory.utils.config_section import ConfigSection
from ivory.utils.opt_helper import get_opt_parameter_dict, get_section_parameter_name_from_opt, get_all_longopts


class TestOptHelper:
    def test_get_all_longopts(self):
        mock_config_sections = {
            'Section': ConfigSection(a=1)
        }
        all_longopts = get_all_longopts(config_sections=mock_config_sections)[0]
        assert 'Section-a=' == all_longopts

    def test_get_section_parameter_name_from_opt(self):
        section_name, parameter_name, parameter_value = get_section_parameter_name_from_opt(
            ('--ExamplePlugin-example-parameter', '2')
        )
        assert section_name == 'ExamplePlugin'
        assert parameter_name == 'example_parameter'
        assert parameter_value == '2'

    def test_get_opt_parameter_dict(self):
        mock_opt_list = [('--Section-parameter', '99')]
        results = get_opt_parameter_dict(opt_list=mock_opt_list)
        expects = ['Section', 'parameter' '99']
        for expect, result in zip(expects, results):
            assert expect == result


if __name__ == '__main__':
    pytest.main()
