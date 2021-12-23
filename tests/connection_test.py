import allure
import pytest
from pytest_testrail.plugin import Testrail


def test_failed():
    assert False


def test_passed():
    assert True

@Testrail.case_id(1531)
@pytest.mark.luboi
@pytest.mark.parametrize('common_arg2', [10000, 7887])
@pytest.mark.parametrize(("n", "expected"), [(10000, 20000), pytest.param(1, 10001, marks=pytest.mark.luboi), (2, 3)])
def test_increment(n, expected, common_arg2):
    assert n + common_arg2 == expected