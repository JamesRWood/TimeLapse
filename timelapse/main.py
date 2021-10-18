import argparse
import time
import multiprocessing as mp
from datetime import datetime, timedelta

from timelapse.log_manager import LogManager
from timelapse.timer.timer_process import TimerProcess
from timelapse.camera.camera_process import CameraProcess
from timelapse.json_config_manager import JsonConfigManager


class Main(object):
    def __init__(self):
        self.run_complete = mp.Event()

    def main(self, argv):
        config = JsonConfigManager()
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('--debug', action='store_true', help='run in debug mode')

        parsed_args, unparsed_args = arg_parser.parse_known_args(argv)
        argv = argv[:1] + unparsed_args

        LogManager.log_info(__name__, 'Application starting')

        try:
            if parsed_args.debug:
                current_time = datetime.now()
                LogManager.log_info(__name__, 'Running in DEBUG mode')
                config.run_configuration.debug_mode = True
                config.run_configuration.schedules[0].start = (current_time + timedelta(seconds=5))
                config.run_configuration.schedules[0].end = (current_time + timedelta(seconds=35))
                config.run_configuration.schedules[1].start = (current_time + timedelta(minutes=1, seconds=5))
                config.run_configuration.schedules[1].end = (current_time + timedelta(minutes=1, seconds=35))

            timer_queue = mp.JoinableQueue()

            timer_process = TimerProcess(timer_queue, self, config)
            camera_process = CameraProcess(timer_queue, self, config)

            procs = [timer_process, camera_process]

            try:
                for proc in procs:
                    proc.start()

                for proc in procs:
                    proc.join()
            except Exception as e:
                LogManager.log_error(__name__, f'{e}')

            self.run_complete.wait()

            # Allow processes to dispose of resources prior to termination
            time.sleep(2)

        except Exception as e:
            LogManager.log_error(__name__, f'{e}')

        except KeyboardInterrupt:
            LogManager.log_info(__name__, 'Keyboard interrupt occurred, closing application')

        self._terminate_processes(procs)

    def _terminate_processes(self, processes):
        for proc in processes:
            proc.terminate()
            LogManager.log_info(__name__, f'Process terminated: {proc.name}')