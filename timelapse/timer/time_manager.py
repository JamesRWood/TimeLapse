import time, sched

from multiprocessing import JoinableQueue
from typing import Type
from logging import Logger
from datetime import datetime

from timelapse.config.config_manager import ConfigManager
from timelapse.messages import CaptureMessage
from timelapse.camera.capture_mode import CaptureMode

class TimeManager():
    def __init__(self, logger: Type[Logger], config: Type[ConfigManager], messageQueue: Type[JoinableQueue]):
        self._logger = logger
        self._config = config
        self._messageQueue = messageQueue
        self._sched = sched.scheduler(time.time, time.sleep)
        self._interval = config.getInt('run', 'interval')
        self._time_format = '%d/%m/%Y_%H:%M:%S'
        self._start_time = datetime.strptime(self._config.get('run', 'start'), self._time_format)
        self._end_time = datetime.strptime(self._config.get('run', 'end'), self._time_format)
        self._debugMode = config.getBoolean('run', 'debug_mode')

    def run(self):
        if self._debugMode == True:
            print('Start time scheduled: ' + self._start_time.strftime(self._time_format))
            print('End time scheduled: ' + self._end_time.strftime(self._time_format))

        self._begin_timer()        

    def _queue_capture(self):
        if datetime.now() < self._end_time:
            self._messageQueue.put(CaptureMessage(CaptureMode.Single))
            self._sched.enter(self._interval, 1, self._queue_capture)
        else:
            if self._debugMode == True:
                print('Run complete.')

    def _begin_timer(self):
        current_datetime = datetime.now()
        if current_datetime > self._start_time:
            self._sched.enter(0, 1, self._queue_capture)
            self._sched.run()
        else:
            diff = self._start_time - current_datetime
            print(diff.total_seconds())
            time.sleep(diff.total_seconds())
            self._begin_timer()

