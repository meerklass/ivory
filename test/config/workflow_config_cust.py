from ivory.utils.config_section import ConfigSection

Pipeline = ConfigSection(
    context_provider="ivory.context_provider.PickleContextProvider",
    ctx_file_name="le_cxt.dump",
    plugins=["test.plugin.simple_plugin"],
)

SimplePlugin = ConfigSection(value=1)
