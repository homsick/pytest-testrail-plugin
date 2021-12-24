from pytest_testrail.plugin import TestRailAPISingle
from pytest_testrail.config import CONFIG


def pytest_addoption(parser):
    parser.addoption(
        "--testrail", action='store_true', help="Взаимодействие с TestRail")


def pytest_configure(config):
    if config.getoption('--testrail'):
        config.pluginmanager.register(TestRailAPISingle(tr_name=None, project_id=CONFIG.TESTRAIL_PROJECT_ID,
                                                        milestone_id=CONFIG.TESTRAIL_MILESTONE_ID, include_all=False))
