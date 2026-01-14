import pytest

from ivory.utils.infer_type import InferType


class TestInferType:
    def test_infer_type(self):
        values = [1, 1.0, "1", "1.", True, "True", "false", "1,2", "[1,2]", [1, "chicago"], None, "null"]
        expect = [1, 1.0, 1, 1.0, True, True, False, [1, 2], [1.0, 2.0], [1, "chicago"], None, None]
        for value, expect in zip(values, expect):
            inferred = InferType.infer_type(value)
            assert inferred == expect
            assert isinstance(inferred, type(expect))


if __name__ == "__main__":
    pytest.main()
