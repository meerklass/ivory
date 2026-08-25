import pytest

from ivory.utils.classproperty import classproperty
from ivory.utils.config_section import ConfigSection


class _Base:
    @classproperty
    def name(cls):
        return cls.__name__


class _Sub(_Base):
    pass


class TestClassProperty:
    def test_class_level_access(self):
        assert _Base.name == "_Base"

    def test_instance_level_access(self):
        """Covers the `owner is None` branch: `__get__` is called with `owner=None`
        when accessed off an instance, and must fall back to `type(obj)`."""
        assert _Base().name == "_Base"

    def test_inherited_class_returns_subclass_name(self):
        assert _Sub.name == "_Sub"
        assert _Sub().name == "_Sub"

    def test_does_not_require_instantiation(self):
        # A classproperty must be usable on the class itself, unlike a plain `@property`.
        called = []

        class WithSideEffect:
            @classproperty
            def value(cls):
                called.append(cls)
                return 42

        assert WithSideEffect.value == 42
        assert called == [WithSideEffect]


class TestConfigSectionName:
    """`ConfigSection.name` is the one real, in-repo consumer of `classproperty` besides
    `AbstractPlugin.name` (covered indirectly via `tests/test_abstract_plugin.py`)."""

    def test_class_level(self):
        assert ConfigSection.name == "ConfigSection"

    def test_instance_level(self):
        assert ConfigSection().name == "ConfigSection"

    def test_subclass(self):
        class MyConfigSection(ConfigSection):
            pass

        assert MyConfigSection.name == "MyConfigSection"
        assert MyConfigSection().name == "MyConfigSection"


if __name__ == "__main__":
    pytest.main()
