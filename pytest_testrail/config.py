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
        self.TEST_RAIL_URL: str = config_get(config.get, section, 'URL')
        self.TEST_RAIL_EMAIL: str = config_get(config.get, section, 'EMAIL')
        self.TEST_RAIL_PASSWORD: str = config_get(config.get, section, 'PASSWORD')
        self.TEST_RAIL_TAG_GROUP_ID: str = config_get(config.get, section, 'TAG_GROUP_ID')
        self.TEST_RAIL_TAG_CASE_ID: str = config_get(config.get, section, 'TAG_CASE_ID')
        self.TEST_RAIL_AUTOTEST_PREFIX: str = config_get(config.get, section, 'AUTOTEST_PREFIX')


CONFIG: Config = Config()
