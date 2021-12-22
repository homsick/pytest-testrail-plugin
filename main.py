from testrail_api import TestRailAPI

from pytest_testrail.plugin import *
from pytest_testrail.config import CONFIG
import urllib3
import datetime
import pytest


class TdssdestRailAPISingle(TestRailAPI):

    # Переменные необходимые для ТестРейла
    TEMPLATE_ID_TEXT = 1 # Виды кейсов
    TYPE_ID_AUTOMATED = 3 # Типы кейсов
    STATUS_ACTUAL = 1 # Кастомные статусы
    FILES = 0

    def __init__(self):
        super().__init__(CONFIG.TEST_RAIL_URL, CONFIG.TEST_RAIL_EMAIL, CONFIG.TEST_RAIL_PASSWORD, verify=False)

        self.milestone_id = 0 # type: int
        self.run_id = 0 # type: int

    def create_cases_from_tests(self, tests: list, tags: list = None): # Создание кейсов в ТестРайл
        section_id = 1 #self.get_id_by_tag(CONFIG.TEST_RAIL_TAG_GROUP_ID)
        case_id = 0
        for file in tests: # Цикл тестовых файлов
            f = open(f'{CONFIG.TEST_RAIL_TEST_DIR}{CONFIG.TEST_RAIL_FILES}.py', 'r')
            replacement = ""
            for line in f: # Цикл строк в тестовом файле
                line = line.strip()
                print(line)
                changes = line.replace("@_case_id_", "@_case_id_88455")
                replacement = replacement + changes + "\n"
                f.close()
                # opening the file in write mode
                # fout = open(f'{CONFIG.TEST_RAIL_TEST_DIR}{CONFIG.TEST_RAIL_FILES}.py', "w")
                # fout.write(replacement)
                # fout.close()


                title = "Имя тест кейса" + "/" + "Имя сценария"
                if case_id:
                    self.cases.update(case_id, title=title)
                else:
                    case = self.cases.add_case(
                        section_id=section_id, title=title,
                        template_id=self.TEMPLATE_ID_TEXT, type_id=self.TYPE_ID_AUTOMATED,
                        custom_tcstatus=self.STATUS_ACTUAL)
                    case_id = case.get('id')

    def set_milestone(self, id_ms): # Установка майлстоуна
        self.milestone_id = id_ms

    def d(self, milestone_id): #Создание прогона
        self.milestome_id = milestone_id # а нужно ли?
        if not self.milestone_id:
            return

        milestone_name = self.milestone.get_milestone(self.milestone_id).get('name')

if __name__ == '__main__':
    pass
    pytest.main(["--tr_add_cases"])
    # print(get_collected_testes())
    #
    #tr.cllll()
    #tr.create_cases_from_tests(CONFIG.TEST_RAIL_FILES)
    #print(pytest.main(["tests/connection_test.py"]))
    #pytest.main(["tests/connection_test.py","-v"])
    #pytest.main(["-q"])

