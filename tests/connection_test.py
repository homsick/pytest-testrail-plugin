import pytest
from pytest_testrail.plugin import testrail


@testrail.case_id(92)
def test_failed():
    assert False


@testrail.case_id(91)
def test_passed():
    assert True


@testrail.case_id(90)
@testrail.case_id(89)
@testrail.case_id(88)
@pytest.mark.parametrize(("n", "expected"), [(1, 2), pytest.param(1, 3, marks=pytest.mark.skip), (2, 3)])
def test_increment(n, expected):
    assert n + 1 == expected