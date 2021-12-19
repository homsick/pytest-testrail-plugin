import allure
import pytest

from pytest_testrail.plugin import testrail


@testrail.case_id(87)
def test_bar():
    pass


class TestGroup:

    @testrail.case_id(86)
    @allure.title("sadas")
    def test_the_power(self):
        print(self)

    @testrail.case_id(85)
    def test_something_else(self):
        assert True

@testrail.case_id(102)
    @pytest.mark.luboi
    @pytest.mark.parametrize("a, b, expected_result", [(5, 10, 150), (10, 51, 150)])
    def test_something_wrong(self, a, b, expected_result):
        diff = a - b
        assert diff == expected_result


@testrail.case_id(82)
def test_foo():
    x = 1+3
    zhopa = x+21

    assert zhopa == 2


@testrail.case_id(81)
def test_functionality1():
    print("World")
    assert True
