from ivy import context


class ContextSensitiveTest:
    """
    Simple base class which resets the context after method execution
    """

    def teardown_method(self, method):
        context.global_ctx = None
