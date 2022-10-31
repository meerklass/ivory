from typing import Optional


class InferType:
    """ Helper class to read types correctly from command line. """

    @staticmethod
    def boolify(string_: str):
        """ Turns `string_` to bool if possible. Otherwise raises `ValueError`. """
        if string_.lower() == 'true':
            return True
        if string_.lower() == 'false':
            return False
        raise ValueError('Not Boolean Value!')

    @staticmethod
    def noneify(string_: str):
        """ Turns `string_` into None` if it matches the criteria. """
        if string_.lower() in ['none', 'null']:
            return
        raise ValueError('Input does not represent `None`!')

    @classmethod
    def listify(cls, string_: str):
        """ Turns `string_` to a list if possible, otherwise raises `ValueError`. """
        string_ = string_.strip(']').strip('[')
        if (string_.count(',') <= 0):
            raise ValueError('Not a string!')
        return [cls.infer_type(element, None) for element in string_.split(',')]

    @classmethod
    def infer_type(cls, string_: str, config_value: Optional[str] = None):
        """ Guesses the str representation of the `string_` type with help of its type in the config. """
        if config_value is not None:
            return cls._type_converter_dict[type(config_value)](string_)
        string_ = str(string_).replace("'", "").replace(' ', '')  # important if the parameters aren't strings...
        for caster in (cls.boolify, int, float, cls.listify, cls.noneify):
            try:
                return caster(string_)
            except ValueError or TypeError:
                pass
        return string_

    @classmethod
    @property
    def _type_converter_dict(cls):
        """ Dict to convert types. """
        return {
            str: str,
            bool: cls.boolify,
            list: cls.listify,
            int: int,
            float: float,
            None: cls.noneify
        }
