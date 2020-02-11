import multiprocessing as mp

from multiprocessing import JoinableQueue
from typing import Type

from timelapse.log_manager import LogManager
from timelapse.timer.time_manager import TimeManager

class TimerProcess(mp.Process):
    def __init__(self, timer_p_pipe, caller):
        super(TimerProcess, self).__init__()
        self.timer_p_pipe = timer_p_pipe
        self.caller = caller

    def run(self):
        try:
            TimeManager(self.timer_p_pipe).run()
        finally:
            LogManager.log_info(__name__, 'TimerProcess closing')
            self.caller.run_complete.set()