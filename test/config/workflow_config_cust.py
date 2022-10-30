Pipeline = dict(
    context_provider="ivy.context_provider.PickleContextProvider",
    ctx_file_name="le_cxt.dump",
    plugins=["test.plugin.simple_plugin"],
)

SimplePlugin = dict(
    value=1
)
