import allure
import pytest

from pytest_testrail.plugin import Testrail


@Testrail.case_id(463)
def test_bar():
    pass


class TestGroup:

    @Testrail.case_id(462)
    @allure.title('dsjkfkoajsdkfjkdsfjdsfs')
    @pytest.mark.luboi
    def test_the_power(self):
      print(self)

    @Testrail.case_id(461)
    def test_something_else(self):
        assert True

    @Testrail.case_id(460)
    @pytest.mark.parametrize("a, b, expected_result", [(5, 10, 150), (10, 51, 150)])
    def test_something_wrong(self, a, b, expected_result):
        diff = a - b
        assert diff == expected_result


@Testrail.case_id(459)
def test_foo():
    x = 1+3
    zhopa = x+21
    assert zhopa == 2


@Testrail.case_id(458)
def test_functionality1():
    print("World")
    assert True