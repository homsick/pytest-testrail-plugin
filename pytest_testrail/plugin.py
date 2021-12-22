import datetime
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


class TestRailAPISingle(TestRailAPI):

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
        self.project_id = 1
        self.list_cases_id = []

    @pytest.hookimpl(trylast=True)
    def pytest_collection_modifyitems(self, session, config, items):
        urllib3.disable_warnings()
        if config.getoption('tr_add_cases'):

            sajkdhkashdka = get_tests_info(items)  # Перевернутый кортеж тестов c информацией

            section_id = self.SECTION_ID  # group_id
            case_tag = self.CASE_TAG
            list_cases_id = []  # Список id всех собранных тестов

            for item in sajkdhkashdka:
                print(item[0])

            # Перебор списка всех тестов с информацией
            for item in sajkdhkashdka:
                test_location = item[0]  # Полный путь к тесту
                file_name = item[1]  # Имя файла
                test_name = item[2]  # Имя теста
                test_line = item[3]  # Строка на которой находится тест
                list_test_markers = item[4]  # Список маркеров теста
                source_code = item[5]  # Полный текст теста
                title = item[6]  # Заголовок теста
                # title = f'{test_location} | {test_class}{test_name}'  # Генерируемый заголовок для TestRail
                testrail_case_id = 0  # case_id для TestRail

                print(f'\nПУТЬ - {test_location}\n'
                      f'ИМЯ ФАЙЛА - {file_name}\n'
                      f'ИМЯ КЕЙСА - {test_name}\n'                      
                      f'СТРОКА - {test_line}\n'
                      f'СПИСОК МАРКЕРОВ - {list_test_markers}\n'
                      f'ПОЛНЫЙ ТЕКСТ ТЕСТА - \n{source_code}'
                      )

                find_case_id_marker = False  # Проверка найден ли marker с case_id
                param_with_case_id = False

                # Перебираем маркеры текущего теста и ищем маркер case_id с аргументом id
                for marker in list_test_markers:
                    if marker.name == "case_id" and marker.args[0] != "":
                        find_case_id_marker = True
                        break
                # Проверка если тест параметризированный есть ли в нем case_id
                    # Если есть маркер parametrize
                    if marker.name == "parametrize":
                        file = open(test_location, 'r', encoding="utf8")
                        lines = [line for line in file]  # Все стройки файла
                        needed_line = lines[test_line]
                        if case_tag in needed_line:
                            param_with_case_id = True
                        file.close()

                # Если есть маркер case_id с аргументом id
                if find_case_id_marker == True:
                    testrail_case_id = marker.args[0]
                    print(f'Данный кейс уже имеет case_id({testrail_case_id})')

                    # Обновление заголовка у кейса в TestRail
                    self.cases.update_case(testrail_case_id, title=title)
                    list_cases_id.append(testrail_case_id)
                # Если маркера case_id нет
                else:

                    # Создание кейса в TestRail
                    # Если параметризированный тест не имеет case_id

                    # hsdkfhsd = []
                    # hsdkfhsd[0] = {
                    #     "content": "Open home page",
                    #     "additional_info": "",
                    #     "expected": "",
                    #     "refs": ""
                    # }
                    # hsdkfhsd[1] = {
                    #     "content": "Open home page",
                    #     "additional_info": "",
                    #     "expected": "",
                    #     "refs": ""
                    # }
                    custom_steps_separated = [
                        {
                            "content": "Open home page",
                            "additional_info": "",
                            "expected": "",
                            "refs": ""
                        },
                        {
                            "content": "[54546]",
                            "additional_info": "",
                            "expected": "",
                            "refs": ""
                        }
                    ]
                    if param_with_case_id == False:
                        print('Тест без case_id. Создание case_id в TestRail...')
                        case = self.cases.add_case(
                            section_id=section_id, title=title,
                            template_id=self.TEMPLATE_ID_STEPS, type_id=self.TYPE_ID_AUTOMATED,
                            custom_tcstatus=self.STATUS_ACTUAL, custom_steps=source_code, custom_steps_separated=custom_steps_separated)
                        testrail_case_id = case.get('id')
                        list_cases_id.append(testrail_case_id)

                        # Добавление маркера case_id в файл
                        file = open(test_location, 'r', encoding="utf8")
                        lines = [line for line in file]  # Все стройки файла
                        lines[test_line - 1] = f'\n{get_spaces(lines[test_line])}{lines[test_line - 1].replace(lines[test_line - 1], case_tag)}({str(testrail_case_id)})\n'
                        with open(test_location, 'w', encoding="utf8") as file:
                            file.write(''.join(lines))

            print(f'Список всех найденных case_id - {list_cases_id}')
        self.milestone_id = 1
        milestone_name = self.milestones.get_milestone(self.milestone_id)
        run = self.runs.add_run(
            self.project_id,
            name=f'{datetime.datetime.now()}', #name=f'{CONFIG.TEST_RAIL_AUTOTEST_PREFIX} {milestone_name} ___ {datetime.datetime.now()}',
            milestone_id=self.milestone_id, include_all=False)
        self.run_id = run.get('id')
        self.runs.update_run(self.run_id, case_ids=list_cases_id)
        self.runs.close_run(self.run_id)
        self.list_cases_id = list_cases_id

    # def after(self):
    #     if not self.milestone_id:
    #         return
    #
    #     for case_id in list_cases_id:
    #         status_id_case = TESTRAIL_TEST_STATUS(1)
    #         if False:
    #             status_id_case = TESTRAIL_TEST_STATUS(5)
    #         self.results.add_result_for_case(self.run_id, case_id, status_id=status_id_case)

    # def create_test_run(self, project_id, suite_id, include_all,
    #                     testrun_name, tr_keys, milestone_id, description=''):
    #     """
    #     Создание тестового прогона
    #     Create testrun with ids collected from markers.
    #
    #     :param tr_keys: collected testrail ids.
    #     """
    #     data = {
    #         'suite_id': suite_id,
    #         'name': testrun_name,
    #         'description': description,
    #         'assignedto_id': assign_user_id,
    #         'include_all': include_all,
    #         'case_ids': tr_keys,
    #         'milestone_id': milestone_id
    #     }
    #
    #     response = self.client.send_post(
    #         ADD_TESTRUN_URL.format(project_id),
    #         data,
    #         cert_check=self.cert_check
    #     )
    #     error = self.client.get_error(response)
    #     if error:
    #         print('[{}] Failed to create testrun: "{}"'.format(TESTRAIL_PREFIX, error))
    #     else:
    #         self.testrun_id = response['id']
    #         print('[{}] New testrun created with name "{}" and ID={}'.format(TESTRAIL_PREFIX,
    #                                                                          testrun_name,
    #                                                                          self.testrun_id))


def get_tests_info(items):
    """
    Возвращает кортеж тестов с информацией
    Return Tuple of Pytest nodes and TestRail ids from pytests markers"""
    tests_with_info = []  # Кортеж тестов c информацией
    for item in items:
        data = [item.location[0],  # Полный путь к тесту
                item.module.__name__,  # Имя файла
                item.name,  # Имя теста
                item.location[1],  # Строка на которой находится тест
                item.own_markers,  # Список маркеров теста
                inspect.getsource(item.obj),  # Полный текст теста
                item.nodeid  # Заголовок теста
                ]
        tests_with_info.append(data)
    # КОСТЫЛЬ ДЛЯ ПЕРЕВОРОТА кортежа
    reversed_tests_with_info = []  # Перевернутый кортеж тестов c информацией
    for item in reversed(tests_with_info):
        reversed_tests_with_info.append(item)
    return reversed_tests_with_info


# def get_collected_testes():
#     return TestRailAPISingle.list_cases_id


def get_spaces(string):
    space_prefix = "    "
    return " "*(len(string) - len(string.lstrip(' ')))


class PyTestRailPlugin(object):
    def __init__(self,test):
        test = 1
