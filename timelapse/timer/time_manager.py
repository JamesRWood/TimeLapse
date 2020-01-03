import time, sched, decimal

from multiprocessing import JoinableQueue
from typing import Type
from datetime import datetime

from timelapse.log_manager import LogManager
from timelapse.config.config_manager import ConfigManager
from timelapse.messages import CaptureMessage, RunCompleteMessage
from timelapse.camera.capture_mode import CaptureMode

class TimeManager():
    def __init__(self, config: Type[ConfigManager], messageQueue: Type[JoinableQueue]):        
        self._config = config
        self._messageQueue = messageQueue
        self._sched = sched.scheduler(time.time, time.sleep)
        self._interval = config.getInt('run', 'interval')
        self._time_format = '%d/%m/%Y_%H:%M:%S'
        self._start_time = datetime.strptime(self._config.get('run', 'start'), self._time_format)
        self._end_time = datetime.strptime(self._config.get('run', 'end'), self._time_format)
        self._debugMode = config.getBoolean('run', 'debug_mode')

    def run(self):
        if self._debugMode:
            LogManager.log_info(__name__, 'Start time scheduled: ' + self._start_time.strftime(self._time_format))
            LogManager.log_info(__name__, 'End time scheduled: ' + self._end_time.strftime(self._time_format))

        self._begin_timer()        

    def _queue_capture(self):
        if datetime.now() < self._end_time:
            self._messageQueue.put(CaptureMessage(CaptureMode.Single))
            self._sched.enter(self._interval, 1, self._queue_capture)
        else:
            self._messageQueue.put(RunCompleteMessage())
            LogManager.log_info(__name__, 'Run complete.')

    def _begin_timer(self):
        current_datetime = datetime.now()
        if current_datetime > self._start_time:
            self._sched.enter(0, 1, self._queue_capture)
            self._sched.run()
        else:            
            diff = self._start_time - current_datetime
            diff_seconds = diff.total_seconds()
            LogManager.log_info(__name__, '%s: %.2fs' % ('Time until scheduled start', diff_seconds))
            time.sleep(diff_seconds)
            self._begin_timer()


