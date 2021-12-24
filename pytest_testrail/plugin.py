from datetime import datetime
import inspect
import pytest

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


class testrail(object):

    @staticmethod
    def case_id(case_id):
        """ Декоратор для маркировки тестов case_id """
        return pytest.mark.case_id(case_id)


def rewrite_test_file(path, line, testrail_case_id):
    """ Перезаписывание тестового файла """
    file = open(path, 'r', encoding="utf8")
    lines = [line for line in file]  # Все строки файла
    # 1 Получение количества пробелов на строке ниже
    # 2 Замена текущей строки
    # 3 Добавление case_id
    lines[line] = f'\n{get_spaces(lines[line + 1])}' \
                  f'{lines[line].replace(lines[line], CONFIG.TESTRAIL_MARKER_CASE_ID)}' \
                  f'({testrail_case_id})\n'
    with open(path, 'w', encoding="utf8") as file:
        file.write(''.join(lines))


class TestRailAPISingle(TestRailAPI):
    # Шаблоны кейсов
    TEMPLATE_ID_EXPLORATION = 3
    TEMPLATE_ID_STEPS = 2
    TEMPLATE_ID_TEXT = 1

    TYPE_ID_AUTOMATED = 3  # Типы тестов
    STATUS_ACTUAL = 1  # Кастомные статусы

    def __init__(self, project_id, include_all, tr_name, testrun_id=0, milestone_id=None):
        super().__init__(CONFIG.TESTRAIL_URL, CONFIG.TESTRAIL_EMAIL, CONFIG.TESTRAIL_PASSWORD, verify=False)

        self.project_id = project_id
        self.include_all = include_all
        self.testrun_id = testrun_id
        self.milestone_id = milestone_id
        self.testrun_name = tr_name
        self.test_results = []

    @pytest.hookimpl(trylast=True)
    def pytest_collection_modifyitems(self, config, items):
        """ Сбор тестов """
        urllib3.disable_warnings()
        if config.getoption('testrail'):
            collected_tests = []
            collected_tests_for_file = []
            custom_steps_separated = []
            for test in items:
                find_marker_case_id_parent = False
                find_marker_case_id = False
                source_code = inspect.getsource(test.obj)
                path = test.location[0]
                line = test.location[1] - 1
                testrail_case_id = 0
                # Для параметризированных тестов
                if 'callspec' in dir(test):
                    title = test.callspec.metafunc.definition.nodeid
                    markers_child = test.own_markers
                    for marker in markers_child:
                        if marker.name == "allure_display_name":
                            title = marker.args[0]
                        if marker.name == "case_id":
                            testrail_case_id = marker.args[0]
                            if not testrail_case_id in collected_tests:
                                custom_steps_separated = []

                    markers_parent = test.callspec.metafunc.definition.own_markers
                    for marker in markers_parent:
                        if marker.name == "case_id":
                            find_marker_case_id_parent = True
                            testrail_case_id = marker.args[0]
                            collected_tests.append(testrail_case_id)
                            break
                    # Обновление параметризированного теста в TestRail
                    if find_marker_case_id_parent:
                        print(f'Параметризированный тест уже имеет case_id({testrail_case_id}).'
                              f' Обновление теста в TestRail...')
                        if testrail_case_id in collected_tests:
                            custom_steps_separated += [
                                {
                                    "content": f'{test.callspec.params}',
                                    "additional_info": "",
                                    "expected": "",
                                    "refs": ""
                                }
                            ]
                            self.cases.update_case(testrail_case_id, title=title,
                                                   custom_steps=source_code,
                                                   custom_steps_separated=custom_steps_separated)
                            collected_tests.append(testrail_case_id)
                            print(f'Параметризированный тест с case_id({testrail_case_id}). Обновлен.')
                    # Создание параметризированного теста в TestRail
                    else:
                        print('Параметризированный тест без case_id. Создание case_id в TestRail...')
                        custom_steps_separated = [
                            {
                                "content": f'{test.callspec.params}',
                                "additional_info": "",
                                "expected": "",
                                "refs": ""
                            }
                        ]

                        case = self.cases.add_case(
                            section_id=CONFIG.TESTRAIL_SECTION_ID, title=title,
                            template_id=self.TEMPLATE_ID_STEPS, type_id=self.TYPE_ID_AUTOMATED,
                            custom_tcstatus=self.STATUS_ACTUAL, custom_steps=source_code,
                            custom_steps_separated=custom_steps_separated)
                        testrail_case_id = case.get('id')
                        print(f'Создан параметризированный тест с case_id({testrail_case_id})')
                        test.callspec.metafunc.definition.add_marker(pytest.mark.case_id(testrail_case_id))
                        collected_tests.append(testrail_case_id)
                        collected_tests_for_file.append([path, line, testrail_case_id])
                # Для обычных тестов
                else:
                    title = test.nodeid
                    markers_simple = test.own_markers
                    for marker in markers_simple:
                        if marker.name == "case_id":
                            if marker.name == "allure_display_name":
                                title = marker.args[0]
                            testrail_case_id = marker.args[0]
                            find_marker_case_id = True
                    # Обновление обычного теста в TestRail
                    if find_marker_case_id:
                        print(f'Обычный тест уже имеет case_id({testrail_case_id}). Обновление теста в TestRail...')
                        self.cases.update_case(testrail_case_id, title=title,
                                               custom_steps=source_code)
                        collected_tests.append(testrail_case_id)
                        print(f'Обычный тест с case_id({testrail_case_id}). Обновлен.')
                    # Создание обычного теста в TestRail
                    else:
                        print('Обычный тест без case_id. Создание case_id в TestRail...')
                        case = self.cases.add_case(
                            section_id=CONFIG.TESTRAIL_SECTION_ID, title=title,
                            template_id=self.TEMPLATE_ID_STEPS, type_id=self.TYPE_ID_AUTOMATED,
                            custom_tcstatus=self.STATUS_ACTUAL, custom_steps=source_code)
                        testrail_case_id = case.get('id')
                        print(f'Создан обычный тест с case_id({testrail_case_id})')
                        test.add_marker(pytest.mark.case_id(testrail_case_id))
                        collected_tests.append(testrail_case_id)
                        collected_tests_for_file.append([path, line, testrail_case_id])

            if self.testrun_name is None:
                self.testrun_name = f'{CONFIG.TESTRAIL_AUTOTEST_PREFIX} {str(datetime.now())}'

            collected_tests = list(set(collected_tests))
            for test in reversed(collected_tests_for_file):
                rewrite_test_file(test[0], test[1], test[2])
            self.testrun_id = self.create_test_run(
                self.project_id,
                self.testrun_name,
                self.milestone_id,
                collected_tests,
                self.include_all
            )

    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(self, item):
        """ Сбор результатов тестов """
        outcome = yield
        report = outcome.get_result()  # Отчёт с результатами теста
        if report.when == 'call':
            parameterized_test = False
            status_id = PYTEST_TO_TESTRAIL_STATUS[report.outcome]
            steps_status_id = None
            testrail_case_id = [mark.args[0] for mark in item.iter_markers(name="case_id")]
            # Сбор результатов для параметризированных тестов
            if 'callspec' in dir(item):
                steps_status_id = [status_id]
                testrail_case_id = [mark.args[0] for mark in
                                    item.callspec.metafunc.definition.iter_markers(name="case_id")]
                for result in enumerate(self.test_results):
                    if result[1][0] == testrail_case_id[0]:
                        self.test_results[result[0]][1].append(status_id)
                        parameterized_test = True
            # Сбор результатов для обычных тестов
            if not parameterized_test:
                data = [testrail_case_id[0],
                        steps_status_id,
                        status_id]
                self.test_results.append(data)

    @pytest.hookimpl(trylast=True)
    def pytest_terminal_summary(self):
        """ Добавление результатов тестов в тестовый прогон и Закрытие тестового прогона """
        urllib3.disable_warnings()
        self.add_results(self.testrun_id)
        self.close_test_run(self.testrun_id)

    def create_test_run(self, project_id, testrun_name, milestone_id, case_ids, include_all):
        """ Создание тестового прогона """
        data = {
            'name': testrun_name,
            'milestone_id': milestone_id,
            'case_ids': case_ids,
            'include_all': include_all
        }
        run = self.runs.add_run(project_id, **data)
        return run.get('id')

    def add_results(self, testrun_id):
        """ Добавление результатов тестов в тестовый прогон """
        for result in self.test_results:
            testrail_case_id = result[0]
            custom_step_results = []
            steps_status_id = result[1]
            status_id = 0
            # Добавление результата для параметризированного теста
            if steps_status_id:
                for step_status_id in steps_status_id:
                    # Если хоть один шаг провален, весь тест провален
                    if step_status_id == 5:
                        status_id = 5
                    else:
                        status_id = 1
                    custom_step_results += [
                        {
                            "status_id": step_status_id
                        }
                    ]
                self.results.add_result_for_case(testrun_id, case_id=testrail_case_id, status_id=status_id,
                                                 assignedto_id=CONFIG.TESTRAIL_ASSIGNEDTO_ID,
                                                 custom_step_results=custom_step_results)
            # Добавление результата для обычного теста
            else:
                status_id = result[2]
                self.results.add_result_for_case(testrun_id, case_id=testrail_case_id, status_id=status_id,
                                                 assignedto_id=CONFIG.TESTRAIL_ASSIGNEDTO_ID)

    def close_test_run(self, testrun_id):
        """ Закрытие тестового прогона """
        self.runs.close_run(testrun_id)


def get_spaces(string):
    """ Получение количества пробелов в начале строки """
    return " " * (len(string) - len(string.lstrip(' ')))