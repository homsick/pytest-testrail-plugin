import allure
import pytest
from pytest_testrail.plugin import Testrail


@Testrail.case_id(222)
def test_failed():
    assert False


@Testrail.case_id(221)
def test_passed():
    assert True

@Testrail.case_id(236)
@pytest.mark.parametrize('common_arg2', [54654, 7887])
@pytest.mark.parametrize(("n", "expected"), [(1, 2), pytest.param(1, 3, marks=pytest.mark.skip), (2, 3)])
def test_increment(n, expected, common_arg2):
    assert n + 1 + common_arg2== expected