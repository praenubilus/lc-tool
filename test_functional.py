import pytest

pytestmark = pytest.mark.timeout(5)


def test_sample_input():
    v = 1
    assert 1 == v