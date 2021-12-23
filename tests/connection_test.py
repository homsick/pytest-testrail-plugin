import allure
import pytest
from pytest_testrail.plugin import Testrail


@Testrail.case_id(996)
def test_failed():
    assert False


@Testrail.case_id(995)
def test_passed():
    assert True


@Testrail.case_id(1014)
@allure.title('Заголовок взятый из маркера @allure.title')
@allure.title('Заголовок взятый из маркера @allure.title')
@allure.title('Заголовок взятый из маркера @allure.title')
@pytest.mark.parametrize('common_arg2', [10000, 7887])
@pytest.mark.parametrize(("n", "expected"), [(10000, 20000), pytest.param(1, 10001, marks=pytest.mark.luboi), (2, 3)])
def test_increment(n, expected, common_arg2):
    assert n + common_arg2 == expected