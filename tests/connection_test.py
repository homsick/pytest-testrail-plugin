import pytest
from pytest_testrail.plugin import Testrail


@Testrail.case_id(215)
def test_failed():
    assert False


@Testrail.case_id(214)
def test_passed():
    assert True


@Testrail.case_id(213)
@pytest.mark.parametrize(("n", "expected"), [(1, 2), pytest.param(1, 3, marks=pytest.mark.skip), (2, 3)])
def test_increment(n, expected):
    assert n + 1 == expected