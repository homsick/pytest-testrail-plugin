import allure
import pytest

from pytest_testrail.plugin import Testrail


# @Testrail.case_id(488)
# def test_bar():
#     pass


class TestGroup:

    @allure.title('Заголовок взятый из маркера @allure.title')
    def test_the_power(self):
      print(self)

    def test_something_else(self):
        assert True

    @pytest.mark.parametrize("a, b, expected_result", [(5, 10, 143430), (430, 51, 150)])
    def test_something_wrong(self, a, b, expected_result):
        diff = a - b
        assert diff == expected_result


@Testrail.case_id(1530)
@pytest.mark.luboi
def test_foo():
    x = 1+3
    zhopa = x+21
    assert zhopa == 2


def test_functionality1():
    print("World")
    assert True