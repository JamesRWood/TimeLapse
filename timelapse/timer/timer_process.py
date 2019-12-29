import multiprocessing as mp

from multiprocessing import JoinableQueue
from typing import Type
from logging import Logger

from timelapse.config.config_manager import ConfigManager
from timelapse.timer.time_manager import TimeManager

class TimerProcess(mp.Process):
    def __init__(self, logger: Type[Logger], config: Type[ConfigManager], messageQueue: Type[JoinableQueue]):
        super().__init__()        
        self._logger = logger
        self._config = config
        self._messageQueue = messageQueue

    def run(self):
        try:
            TimeManager(self._logger, self._config, self._messageQueue).run()
        except KeyboardInterrupt:
            return
        except:
            self._logger.exception('Exception occurred', exc_info=True)