import pytest
from pytest_testrail.plugin import TestRailAPISingle


def pytest_addoption(parser):
    group = parser.getgroup('TestRail')  # Создание option Group
    group.addoption(
        "--tr_add_cases", action='store_true', help="Add cases from TestRail")


def pytest_configure(config):
    if config.getoption('--tr_add_cases'):
        config.pluginmanager.register(TestRailAPISingle())
