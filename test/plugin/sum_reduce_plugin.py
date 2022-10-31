from ivory.plugin.abstract_plugin import AbstractPlugin


class SumReducePlugin(AbstractPlugin):
    """ Example reduction plugin. """

    def run(self, ctx_list):
        sum_ = 0
        for ctx in ctx_list:
            sum_ += ctx.value

        self.save_to_context(values_sum=sum_)
