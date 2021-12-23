from datetime import datetime
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

DT_FORMAT = '%d-%m-%Y %H:%M:%S'

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

def testrun_name():
    """Возвращает имя прогона с меткой времени"""
    now = datetime.utcnow()
    return 'Automated Run {}'.format(now.strftime(DT_FORMAT))



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

    def __init__(self, project_id, include_all, tr_name, testrun_id=0, milestone_id=None):
        super().__init__(CONFIG.TESTRAIL_URL, CONFIG.TESTRAIL_EMAIL, CONFIG.TESTRAIL_PASSWORD, verify=False)

        self.project_id = project_id
        self.include_all = include_all
        self.testrun_id = testrun_id
        self.milestone_id = milestone_id
        self.testrun_name = tr_name
        self.test_results = []

    def rewrite_test_files(cls, items):
        """Дописывает тестам маркер с case_id"""
        list_cases_id = []  # id тестов
        # Перебор списка всех тестов с информацией
        for item in items:
            test_location = item[0]  # Полный путь к тесту
            test_line = item[1]  # Строка на которой находится тест
            list_test_markers = item[2]  # Список маркеров теста
            source_code = item[3]  # Полный текст теста
            title = item[4]  # Заголовок теста
            idontknow = item[5]  # Для параметризированных кейсов
            mmmmmmmmmmmmmm = item[6]
            testrail_case_id = 0  # case_id для TestRail



            find_case_id_marker = False  # Проверка найден ли marker с case_id
            param_with_case_id = False

            # Перебираем маркеры текущего теста и ищем маркер case_id с аргументом id
            for marker in list_test_markers:
                if marker.name == "allure_display_name":
                    title = marker.args[0]
                if marker.name == "case_id" and marker.args[0] != "":
                    find_case_id_marker = True
                    break

            # Если есть маркер case_id с аргументом id
            if find_case_id_marker == True:
                testrail_case_id = marker.args[0]
                print(f'Данный тест уже имеет case_id({testrail_case_id})')

                # Обновление заголовка у кейса в TestRail
                cls.cases.update_case(testrail_case_id, title=title)
                list_cases_id.append(testrail_case_id)
            # Если маркера case_id нет
            else:
                custom_steps_separated = []
                if not idontknow == None:
                    for gggg in idontknow:
                        custom_steps_separated += [
                            {
                                "content": f'{gggg}',
                                "additional_info": "",
                                "expected": "",
                                "refs": ""
                            }
                        ]

                if param_with_case_id == False:
                    print('Тест без case_id. Создание case_id в TestRail...')
                    case = cls.cases.add_case(
                        section_id=cls.SECTION_ID, title=title,
                        template_id=cls.TEMPLATE_ID_STEPS, type_id=cls.TYPE_ID_AUTOMATED,
                        custom_tcstatus=cls.STATUS_ACTUAL, custom_steps=source_code,
                        custom_steps_separated=custom_steps_separated)
                    testrail_case_id = case.get('id')
                    print(f'Создан тест с case_id({testrail_case_id})')
                    list_cases_id.append(testrail_case_id)

                    # Добавление маркера case_id в файл
                    file = open(test_location, 'r', encoding="utf8")
                    lines = [line for line in file]  # Все стройки файла
                    lines[
                        test_line - 1] = f'\n{get_spaces(lines[test_line])}{lines[test_line - 1].replace(lines[test_line - 1], cls.CASE_TAG)}({str(testrail_case_id)})\n'
                    with open(test_location, 'w', encoding="utf8") as file:
                        file.write(''.join(lines))

                    print(mmmmmmmmmmmmmm.own_markers)
                    print(mmmmmmmmmmmmmm.add_marker(pytest.mark.case_id(testrail_case_id)))
                    print(mmmmmmmmmmmmmm.own_markers)
                    print(list_test_markers)
        return list_cases_id

    def create_test_run(self, project_id, testrun_name, milestone_id, case_ids, include_all):
        """
        Создание тестового прогона.
        Create testrun with ids collected from markers.

        :param case_ids: собранные id тестов.
        """
        data = {
            'name': testrun_name,
            'milestone_id': milestone_id,
            'case_ids': case_ids,
            'include_all': include_all
            }
        run = self.runs.add_run(project_id, **data)

        #print('[{}] New testrun created with name "{}" and ID={}'.format(CONFIG.TESTRAIL_AUTOTEST_PREFIX, 234234))
        return run.get('id')

    def close_test_run(self, testrun_id):
        """
        Закрытие тестового прогона.

        """

        self.runs.close_run(testrun_id)

    @pytest.hookimpl(tryfirst=True)
    def pytest_collection_modifyitems(self, session, config, items):
        urllib3.disable_warnings()
        if config.getoption('tr_add_cases'):
            tests_info = get_tests_info(items)  # Перевернутый кортеж тестов c информацией

            test_case_ids = self.rewrite_test_files(tests_info)  # Список case id

            print(f'Список всех найденных case_id - {test_case_ids}')

            if self.testrun_name is None:
                self.testrun_name = testrun_name()

            self.testrun_id = self.create_test_run(
                self.project_id,
                self.testrun_name,
                self.milestone_id,
                test_case_ids,
                self.include_all
            )


    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        """ Собирает результаты тестов """

        outcome = yield
        rep = outcome.get_result()
        if rep.when == 'call':
            checker_test_parametize = False  # Чекер параметризированный ли кейс

            case_id = [mark.args[0] for mark in item.iter_markers(name="case_id")]
            test_result = rep.outcome
            if test_result == "passed":
                test_result = 1
            else:
                test_result = 5
            steps_result = None

            if 'callspec' in dir(item):
                for ffffff in enumerate(self.test_results):
                    if ffffff[1][0] == case_id:
                        self.test_results[ffffff[0]][2].append(test_result)
                        checker_test_parametize = True
            if checker_test_parametize == False:
                data = [case_id,
                        steps_result,
                        [test_result]]
                self.test_results.append(data)
            print(self.test_results)

    @pytest.hookimpl(trylast=True)
    def pytest_terminal_summary(self):
        urllib3.disable_warnings()
        self.add_results(self.testrun_id)
        self.close_test_run(self.testrun_id)


    def add_results(self, testrun_id):
        print(self.test_results)
        for result in self.test_results:
            custom_step_results = []
            if len(result[2]) > 1:
                status_id = 1
                for step in result[2]:
                    if step == 5:
                        status_id = 5
                    custom_step_results += [
                        {
                            "status_id": step
                        }
                        ]
                print(custom_step_results)
                self.results.add_result_for_case(testrun_id, result[0][0], status_id=status_id, custom_step_results=custom_step_results)
            else:

                self.results.add_result_for_case(testrun_id, result[0][0], status_id=result[2][0])

def get_tests_info(items):
    """
    Возвращает кортеж тестов с информацией
    Return Tuple of Pytest nodes and TestRail ids from pytests markers"""
    tests_with_info = []  # Кортеж тестов c информацией
    for item in items:
        checker_test_parametize = False  # Чекер параметризированный ли кейс
        # Если у теста есть параметр 'callspec'
        if 'callspec' in dir(item):
            test_parametrize = item.callspec.params  # Параметры теста
            for test in enumerate(tests_with_info):
                # Если путь и строка совпадают
                if test[1][0] == item.location[0] and test[1][1] == item.location[1]:
                    # Добавляем параметр
                    tests_with_info[test[0]][5].append(test_parametrize)
                    # Изменяет заголовок теста
                    tests_with_info[test[0]][4] = item.nodeid[:item.nodeid.find('[')]
                    checker_test_parametize = True
        else:
            test_parametrize = None
        if not checker_test_parametize:
            data = [item.location[0],  # Полный путь к тесту
                    item.location[1],  # Строка на которой находится тест
                    item.own_markers,  # Список маркеров теста
                    inspect.getsource(item.obj),  # Полный текст теста
                    item.nodeid,  # Заголовок теста
                    [test_parametrize],  # Для параметризированных кейсов
                    item
                    ]
            tests_with_info.append(data)
    # КОСТЫЛЬ ДЛЯ ПЕРЕВОРОТА кортежа
    reversed_tests_with_info = []  # Перевернутый кортеж тестов c информацией
    for item in reversed(tests_with_info):
        reversed_tests_with_info.append(item)
    print(reversed_tests_with_info)
    return reversed_tests_with_info



# def get_collected_testes():
#     return TestRailAPISingle.list_cases_id

def get_spaces(string):
    space_prefix = "    "
    return " "*(len(string) - len(string.lstrip(' ')))


class PyTestRailPlugin(object):
    def __init__(self,test):
        test = 1
