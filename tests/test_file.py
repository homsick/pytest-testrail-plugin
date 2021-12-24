import allure
import pytest

from pytest_testrail.plugin import testrail


class TestGroup:

    @testrail.case_id(2248)
    @allure.title('Заголовок взятый из маркера @allure.title')
    def test_the_power(self):
        assert True

    @testrail.case_id(2249)
    def test_something_else(self):
        assert True

    @testrail.case_id(2250)
    @pytest.mark.parametrize("ss, ff, frrr", [(5, 10, 45444), (430, 51, 14394545454526), (6666666, 777777777, 21)])
    @pytest.mark.parametrize("a, b, expected_result", [(5, 10, 143430), (430, 51, 150), (34857734, 324234, 234324)])
    def test_something_wrong(self, a, b, expected_result, ss, ff, frrr):
        assert a + b + expected_result + ss + ff == frrr


@testrail.case_id(2251)
def test_functionality1():
    print("World")
    assert True
