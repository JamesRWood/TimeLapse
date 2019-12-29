import configparser
import os

class ConfigManager:
    def __init__(self):
        self._cfg = configparser.ConfigParser(interpolation=None)
        self.loadDefaults()

    def loadDefaults(self):
        fileName = os.path.join(os.path.dirname(__file__), 'defaults.cfg')
        self._cfg.read(fileName)

    def set(self, section, key, value):
        self._cfg[section][key] = value

    def get(self, section, key) -> str:
        return self._cfg[section][key]

    def getInt(self, section, key) -> int:
        return self._cfg.getint(section, key)

    def getBoolean(self, section, key) -> bool:
        return self._cfg.getboolean(section, key)

    def getIntList(self, section, key) -> []:
        output = []
        l = self._cfg[section][key].split(",")
        for x in l:
            output.append(int(x))
        return output
