import configparser
import os


class Config:

    def __init__(self):

        self.PROJECT_DIR: str = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')

        config = configparser.ConfigParser()
        conf_file = os.path.join(self.PROJECT_DIR, 'config.ini').replace('\\', '/')
        config.read(conf_file, encoding='utf8')
        config_assert = []

        def config_get(method, section_, option_):
            if config.has_option(section_, option_):
                return method(section_, option_)
            else:
                config_assert.append(f'Отсутствует конфиг {option_} из секции {section_}')

        # Описание извлеченных параметров смотреть в файле config.ini
        section = 'TESTRAIL'
        self.TESTRAIL_URL: str = config_get(config.get, section, 'URL')
        self.TESTRAIL_EMAIL: str = config_get(config.get, section, 'EMAIL')
        self.TESTRAIL_PASSWORD: str = config_get(config.get, section, 'PASSWORD')

        self.TESTRAIL_AUTOTEST_PREFIX: str = config_get(config.get, section, 'AUTOTEST_PREFIX')
        self.TESTRAIL_MILESTONE_ID: int = config_get(config.get, section, 'MILESTONE_ID')
        self.TESTRAIL_SECTION_ID: int = config_get(config.get, section, 'SECTION_ID')
        self.TESTRAIL_PROJECT_ID: int = config_get(config.get, section, 'PROJECT_ID')
        self.TESTRAIL_ASSIGNEDTO_ID: int = config_get(config.get, section, 'ASSIGNEDTO_ID')
        self.TESTRAIL_MARKER_CASE_ID: str = config_get(config.get, section, 'MARKER_CASE_ID')


CONFIG: Config = Config()
