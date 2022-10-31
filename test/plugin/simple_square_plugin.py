from ivory.plugin.abstract_plugin import AbstractPlugin


class SimpleSquarePlugin(AbstractPlugin):
    """ Plugin that computes the square of ctx.value. """

    def run(self):
        self.ctx.value = self.ctx.value ** 2
