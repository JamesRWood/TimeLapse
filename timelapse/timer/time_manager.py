import time, sched, decimal, sys

from multiprocessing import Pipe
from typing import Type
from datetime import datetime

from timelapse.log_manager import LogManager
from timelapse.config_manager import ConfigManager
from timelapse.messages import CaptureMessage, KillProcessMessage

class TimeManager():
    def __init__(self, timer_queue):
        self._timer_queue = timer_queue
        self._sched = sched.scheduler(time.time, time.sleep)
        self._interval = ConfigManager.getInt('run', 'interval')
        self._time_format = '%d/%m/%Y_%H:%M:%S'
        self._start_time = datetime.strptime(ConfigManager.get('run', 'start'), self._time_format)
        self._end_time = datetime.strptime(ConfigManager.get('run', 'end'), self._time_format)
        self._debugMode = ConfigManager.getBoolean('run', 'debug_mode')

    def run(self):
        if self._debugMode:
            LogManager.log_info(__name__, 'Start time scheduled: ' + self._start_time.strftime(self._time_format))
            LogManager.log_info(__name__, 'End time scheduled: ' + self._end_time.strftime(self._time_format))

        self._begin_timer()
        return

    def _queue_capture(self):
        if datetime.now() < self._end_time:
            if self._timer_queue.empty():
                self._timer_queue.put(CaptureMessage())
                self._sched.enter(self._interval, 1, self._queue_capture)
            else:
                time.sleep(0.2)
                self._queue_capture()
        else:
            LogManager.log_info(__name__, 'Run complete.')
            self._timer_queue.put(KillProcessMessage())
        return

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