import argparse
import logging
import time
import multiprocessing as mp
import logging.config
from os import path
from datetime import datetime, timedelta

from multiprocessing import Pipe

from timelapse.log_manager import LogManager
from timelapse.config_manager import ConfigManager
from timelapse.timer.timer_process import TimerProcess
from timelapse.camera.camera_process import CameraProcess
from timelapse.camera.image_processor import ImageProcessor

class Main(object):
    def __init__(self):
        self.run_complete = mp.Event()

    def main(self, argv):
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('--debug', action='store_true', help='run in debug mode')

        parsed_args, unparsed_args = arg_parser.parse_known_args(argv)
        argv = argv[:1] + unparsed_args

        LogManager.log_info(__name__, 'Application starting')

        try:
            if parsed_args.debug:
                current_time = datetime.now()
                LogManager.log_info(__name__, 'Running in DEBUG mode')
                ConfigManager.set('run', 'debug_mode', 'True')
                ConfigManager.set('run', 'start', (current_time + timedelta(seconds=5)).strftime('%d/%m/%Y_%H:%M:%S'))
                ConfigManager.set('run', 'end', (current_time + timedelta(minutes=1, seconds=5)).strftime('%d/%m/%Y_%H:%M:%S'))

            timer_p_pipe, timer_c_pipe = Pipe()
            img_p_pipe, img_c_pipe = Pipe()

            timer_process = TimerProcess(timer_p_pipe, self)
            camera_process = CameraProcess(timer_c_pipe, img_p_pipe, self)
            image_processor = ImageProcessor(img_c_pipe, self)

            procs = [timer_process, camera_process, image_processor]

            for proc in procs:
                proc.start()

            for proc in procs:
                proc.join()

            self.run_complete.wait()

            # Allow processes to dispose of resources prior to termination
            time.sleep(2)

            for proc in procs:
                proc.terminate()
                LogManager.log_info(__name__, f'Process terminated: {proc.name}')

        except KeyboardInterrupt:
            LogManager.log_info(__name__, 'Keyboard interrupt occurred, closing application')

            for proc in procs:
                proc.terminate()
                LogManager.log_info(__name__, f'Process terminated: {proc.name}')

        except:
            for proc in procs:
                proc.terminate()
                LogManager.log_info(__name__, f'Process terminated: {proc.name}')