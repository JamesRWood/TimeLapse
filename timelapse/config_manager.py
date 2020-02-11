import configparser
import os

class ConfigManager(object):
    _cfg = configparser.ConfigParser(interpolation=None)
    fileName = os.path.join(os.path.dirname(__file__), 'defaults.cfg')
    _cfg.read(fileName)

    @staticmethod
    def set(section, key, value):
        ConfigManager._cfg[section][key] = value

    @staticmethod
    def get(section, key) -> str:
        return ConfigManager._cfg[section][key]

    @staticmethod
    def getInt(section, key) -> int:
        return ConfigManager._cfg.getint(section, key)

    @staticmethod
    def getBoolean(section, key) -> bool:
        return ConfigManager._cfg.getboolean(section, key)

    @staticmethod
    def getIntList(section, key) -> []:
        output = []
        l = ConfigManager._cfg[section][key].split(",")
        for x in l:
            output.append(int(x))
        return output
