import pytest
from pytest_testrail.plugin import Testrail


@Testrail.case_id(133)
def test_failed():
    assert False


@Testrail.case_id(132)
def test_passed():
    assert True


@Testrail.case_id(131)
@pytest.mark.parametrize(("n", "expected"), [(1, 2), pytest.param(1, 3, marks=pytest.mark.skip), (2, 3)])
def test_increment(n, expected):
    assert n + 1 == expected