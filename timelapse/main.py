import argparse
import logging
import multiprocessing as mp
import logging.config
from os import path

from multiprocessing import JoinableQueue

from timelapse.log_manager import LogManager
from timelapse.config.config_manager import ConfigManager
from timelapse.timer.timer_process import TimerProcess
from timelapse.camera.camera_process import CameraProcess

def main(argv):
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--debug', action='store_true', help='run in debug mode')

    parsed_args, unparsed_args = arg_parser.parse_known_args(argv)
    argv = argv[:1] + unparsed_args

    LogManager.log_info(__name__, 'Application starting')

    try:
        message_queue = mp.JoinableQueue()
        config = ConfigManager()

        if parsed_args.debug:
            LogManager.log_error(__name__, 'Running in DEBUG mode')
            config.set('run', 'debug_mode', 'True')

        dependencies = {
            "config": config,
            "messageQueue": message_queue
        }
        
        process_classes = (TimerProcess, CameraProcess)
        procs = [P(**dependencies) for P in process_classes]

        for proc in procs:
            proc.start()

        for proc in procs:
            proc.join()

    except KeyboardInterrupt:
        LogManager.log_info(__name__, 'Keyboard interrupt occurred, closing application')

        for proc in procs:
            proc.terminate()
            LogManager.log_info(__name__, f'Process terminated: {proc.name}')