from ivory.plugin.abstract_plugin import AbstractPlugin


class RangeMapPlugin(AbstractPlugin):
    """ Yields a range of contexts. """

    def run(self):
        """ Get the workload. """
        values = [i for i in range(self.config.values_min, self.config.values_max)]

        for value in values:
            ctx = self.ctx.copy()
            ctx.value = value
            yield ctx
