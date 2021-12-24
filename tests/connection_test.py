import allure
import pytest
from pytest_testrail.plugin import testrail


@testrail.case_id(2245)
def test_failed():
    assert False


@testrail.case_id(2246)
def test_passed():
    assert True


@testrail.case_id(2247)
@allure.title('Заголовок взятый из маркера @allure.title')
@pytest.mark.parametrize('common_arg2', [10000, 7887])
@pytest.mark.parametrize(("n", "expected"), [(10000, 20000), pytest.param(1, 10001), (2, 3)])
def test_increment(n, expected, common_arg2):
    assert n + common_arg2 == expected
