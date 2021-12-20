import fileinput
import inspect
import re
import sys

import pytest
from _pytest._code import getrawcode
from _pytest._io.saferepr import safeformat

from testrail_api import TestRailAPI
from pytest_testrail.config import CONFIG
import urllib3

TESTRAIL_TEST_STATUS = {
    "passed": 1,
    "blocked": 2,
    "untested": 3,
    "retest": 4,
    "failed": 5
}

PYTEST_TO_TESTRAIL_STATUS = {
    "passed": TESTRAIL_TEST_STATUS["passed"],
    "failed": TESTRAIL_TEST_STATUS["failed"],
    "skipped": TESTRAIL_TEST_STATUS["blocked"]
}


class Testrail(object):

    @staticmethod
    def case_id(id):
        """
        Decorator to mark tests with testcase ids.

        ie. @pytestrail.case('C123', 'C12345')

        :return pytest.mark:
        """
        return pytest.mark.case_id(id)


def case_id(*ids):
    return Testrail.case_id(*ids)


# Создание списка всех собранных тестов c информацией
def get_tests(items):

    list_cases = []  # Список всех собранных тестов c информацией
    lines = []
    line_index = 0
    for item in items:

        print(safeformat(item.obj))
        print(item.fixturenames)
        print(item.nodeid)
        if item.cls:
            case_class = f'{item.cls.__name__} | '
        else:
            case_class = ''
        list_cases.append(
            [item.location[0], item.module.__name__, case_class, item.name, item.location[1],
             item.own_markers, inspect.getsource(item.obj)])

    # КОСТЫЛЬ ДЛЯ ПЕРЕВОРОТА СПИСКА
    reversed_list_tests = []  # Перевернутый список всех собранных кейсов c информацией
    for item in reversed(list_cases):
        reversed_list_tests.append(item)
    return reversed_list_tests


class TestRailAPISingle(TestRailAPI, object):

    # Переменные необходимые для ТестРейла

    # Шаблоны кейсов
    TEMPLATE_ID_EXPLORATION = 3
    TEMPLATE_ID_STEPS = 2
    TEMPLATE_ID_TEXT = 1

    TYPE_ID_AUTOMATED = 3  # Типы тестов
    STATUS_ACTUAL = 1  # Кастомные статусы
    SECTION_ID = 1  # или же group_id
    CASE_TAG = '@Testrail.case_id'  #

    def __init__(self):
        super().__init__(CONFIG.TEST_RAIL_URL, CONFIG.TEST_RAIL_EMAIL, CONFIG.TEST_RAIL_PASSWORD, verify=False)

        self.milestone_id = 0  # type: int
        self.run_id = 0  # type: int

    @pytest.hookimpl(trylast=True)
    def pytest_collection_modifyitems(self, session, config, items):
        urllib3.disable_warnings()
        if config.getoption('tr_add_cases'):

            section_id = self.SECTION_ID  # group_id
            case_tag = self.CASE_TAG
            list_cases_id = []  # Список id всех собранных тестов
            reversed_list_tests = get_tests(items)  # Перевернутый список всех собранных кейсов c информацией

            # Перебор списка всех тестов с информацией
            for item in reversed_list_tests:
                test_location = item[0]  # Полный путь к тесту
                file_name = item[1]  # Имя файла
                test_class = item[2]  # Имя класса
                test_name = item[3]  # Имя теста
                test_line = item[4]  # Строка на которой находится тест
                list_test_markers = item[5]  # Список маркеров теста
                source_code = item[6] # Полный текст теста
                testrail_case_id = 0  # case_id для TestRail

                print(f'\nПУТЬ - {test_location}\n'
                      f'ИМЯ ФАЙЛА - {file_name}\n'
                      f'ИМЯ КЛАССА - {test_class}\n'
                      f'ИМЯ КЕЙСА - {test_name}\n'                      
                      f'СТРОКА - {test_line}\n'
                      f'СПИСОК МАРКЕРОВ - {list_test_markers}\n'
                      f'ПОЛНЫЙ ТЕКСТ ТЕСТА - \n{source_code}'
                      )

                find_case_id_marker = False  # Проверка найден ли marker с case_id

                title = f'{test_location} | {test_class}{test_name}'  # Генерируемый заголовок для TestRail

                # Перебираем маркеры текущего теста и ищем маркер case_id с аргументом id
                for marker in list_test_markers:
                    if marker.name == "case_id" and marker.args[0] != "":
                        find_case_id_marker = True
                        break

                # Если есть маркер case_id с аргументом id
                if find_case_id_marker == True:
                    find_case_id_marker = False
                    testrail_case_id = marker.args[0]
                    print(f'Данный кейс уже имеет case_id({testrail_case_id})')

                    # Обновление заголовка у кейса в TestRail
                    self.cases.update_case(testrail_case_id, title=title)
                    list_cases_id.append(testrail_case_id)

                # Если маркера case_id нет
                else:
                    # Проверка если тест параметризированный есть ли в нем case_id
                    param_with_case_id = False
                    for marker in list_test_markers:
                        # Если есть маркер parametrize
                        if marker.name == "parametrize":
                            file = open(test_location, 'r', encoding="utf8")
                            lines = [line for line in file]  # Все стройки файла
                            needed_line = lines[test_line]
                            if case_tag in needed_line:
                                param_with_case_id = True
                            file.close()
                    # Создание кейса в TestRail
                    # Если параметризированный тест не имеет case_id
                    if param_with_case_id == False:
                        print('Тест без case_id. Создание case_id в TestRail...')
                        case = self.cases.add_case(
                            section_id=section_id, title=title,
                            template_id=self.TEMPLATE_ID_STEPS, type_id=self.TYPE_ID_AUTOMATED,
                            custom_tcstatus=self.STATUS_ACTUAL, custom_steps=source_code)
                        testrail_case_id = case.get('id')
                        list_cases_id.append(testrail_case_id)

                        # Добавление маркера case_id в файл
                        file = open(test_location, 'r', encoding="utf8")
                        lines = [line for line in file]  # Все стройки файла
                        lines[test_line - 1] = f'\n{get_spaces(lines[test_line])}{lines[test_line - 1].replace(lines[test_line - 1], case_tag)}({str(testrail_case_id)})\n'
                        with open(test_location, 'w', encoding="utf8") as file:
                            file.write(''.join(lines))

            print(f'Список всех найденных case_id - {list_cases_id}')


def get_spaces(string):
    space_prefix = "    "
    return " "*(len(string) - len(string.lstrip(' ')))


class PyTestRailPlugin(object):
    def __init__(self,test):
        test = 1
