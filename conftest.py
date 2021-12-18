import pytest
from pytest_testrail.plugin import TestRailAPISingle


def pytest_addoption(parser):
    add_cases_from_testrail = parser.getgroup('add_cases_from_testrail')
    add_cases_from_testrail.addoption("--add_cases_from_testrail",
                         default=None,
                         help="Add cases from TestRail")


def pytest_configure(config):
    if config.getoption('--add_cases_from_testrail'):
        config.pluginmanager.register(TestRailAPISingle())
