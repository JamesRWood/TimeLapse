import multiprocessing as mp

from multiprocessing import JoinableQueue
from typing import Type

from timelapse.config.config_manager import ConfigManager
from timelapse.timer.time_manager import TimeManager

class TimerProcess(mp.Process):
    def __init__(self, config: Type[ConfigManager], messageQueue: Type[JoinableQueue]):
        super().__init__()
        self._config = config
        self._messageQueue = messageQueue

    def run(self):
        try:
            TimeManager(self._config, self._messageQueue).run()
        except KeyboardInterrupt:
            return