import sched
import time
from datetime import datetime
from multiprocessing import Process

from timelapse.json_config_manager import JsonConfigManager, RunSchedule
from timelapse.log_manager import LogManager
from timelapse.messages import CaptureMessage, KillProcessMessage


class TimerProcess(Process):
    def __init__(self, timer_queue, caller, config: JsonConfigManager):
        super(TimerProcess, self).__init__()
        self._timer_queue = timer_queue
        self._caller = caller
        self._config = config

    def run(self):
        self._sched = sched.scheduler(time.time, time.sleep)
        self._run_configuration = self._config.run_configuration
        self._interval = self._run_configuration.interval
        self._schedule_cursor = 0

        try:
            if self._run_configuration.debug_mode:
                LogManager.log_info(__name__, f'Number of runs configured: {len(self._run_configuration.schedules)}')
                for i in range(len(self._run_configuration.schedules)):
                    LogManager.log_info(__name__, f'Schedule {i + 1} start time: {self._run_configuration.schedules[i].start}')
                    LogManager.log_info(__name__, f'Schedule {i + 1} end time: {self._run_configuration.schedules[i].end}')

            self._begin_timer(self._run_configuration.schedules[0])
        finally:
            LogManager.log_info(__name__, 'TimerProcess closing')
            self._caller.run_complete.set()

    def _queue_capture(self, schedule: RunSchedule):
        if datetime.now() < schedule.end:
            if self._timer_queue.empty():
                self._timer_queue.put(CaptureMessage())
                self._sched.enter(self._interval, 1, self._queue_capture, kwargs={'schedule': schedule})
            else:
                time.sleep(0.2)
                self._queue_capture(schedule)
        else:
            if self._schedule_cursor == len(self._run_configuration.schedules) - 1:
                LogManager.log_info(__name__, 'Run complete.')
                self._timer_queue.put(KillProcessMessage())
            else:
                self._schedule_cursor = self._schedule_cursor + 1
                self._begin_timer(self._run_configuration.schedules[self._schedule_cursor])
        return

    def _begin_timer(self, schedule: RunSchedule):
        current_datetime = datetime.now()
        if current_datetime > schedule.start:
            LogManager.log_info(__name__, f'Beginning schedule {self._schedule_cursor + 1} run')
            self._sched.enter(0, 1, self._queue_capture, kwargs={'schedule': schedule})
            self._sched.run()
        else:
            diff = schedule.start - current_datetime
            diff_seconds = diff.total_seconds()
            LogManager.log_info(__name__, '%s: %.2fs' % (f'Time until start of schedule {self._schedule_cursor + 1}', diff_seconds))
            time.sleep(diff_seconds)
            self._begin_timer(schedule)
