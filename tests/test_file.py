import allure
import pytest

from pytest_testrail.plugin import Testrail


# @Testrail.case_id(488)
# def test_bar():
#     pass


class TestGroup:

    @Testrail.case_id(993)
    @allure.title('Заголовок взятый из маркера @allure.title')
    def test_the_power(self):
      print(self)

    @Testrail.case_id(992)
    def test_something_else(self):
        assert True

    @Testrail.case_id(991)
    @allure.title('Заголовок взятый из маркера @allure.title')
    @allure.title('Заголовок взятый из маркера @allure.title')
    @pytest.mark.parametrize("a, b, expected_result", [(5, 10, 143430), (430, 51, 150)])
    def test_something_wrong(self, a, b, expected_result):
        diff = a - b
        assert diff == expected_result


@Testrail.case_id(954)
def test_foo():
    x = 1+3
    zhopa = x+21
    assert zhopa == 2


@Testrail.case_id(953)
def test_functionality1():
    print("World")
    assert True