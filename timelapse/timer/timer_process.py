import multiprocessing as mp

from multiprocessing import JoinableQueue
from typing import Type

from timelapse.log_manager import LogManager
from timelapse.timer.time_manager import TimeManager

class TimerProcess(mp.Process):
    def __init__(self, timer_queue, caller):
        super(TimerProcess, self).__init__()
        self._timer_queue = timer_queue
        self.caller = caller

    def run(self):
        try:
            TimeManager(self._timer_queue).run()
        finally:
            LogManager.log_info(__name__, 'TimerProcess closing')
            self.caller.run_complete.set()