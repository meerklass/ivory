import pytest

from ivory.utils.struct import WorkflowState, WorkflowStruct


class TestWorkflowStruct:
    def test_states(self):
        ctx = WorkflowStruct()

        assert ctx.state == WorkflowState.RUN
        ctx.stop()
        assert ctx.state == WorkflowState.STOP
        ctx.reset()
        assert ctx.state == WorkflowState.RUN
        ctx.exit()
        assert ctx.state == WorkflowState.EXIT
        ctx.reset()
        ctx.resume()
        assert ctx.state == WorkflowState.RESUME

    def test_iterator(self):
        ctx = WorkflowStruct()

        assert ctx.iter == 0
        ctx.increment()
        assert ctx.iter == 1

    def teardown(self):
        # tidy up
        print("tearing down " + __name__)
        pass


if __name__ == "__main__":
    pytest.main()
