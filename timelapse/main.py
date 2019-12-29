import argparse
import logging
import multiprocessing as mp

from logging import Logger
from multiprocessing import JoinableQueue

from timelapse.config.config_manager import ConfigManager
from timelapse.timer.timer_process import TimerProcess
from timelapse.camera.camera_process import CameraProcess

def main(argv):
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--debug', action='store_true', help='run in debug mode')

    parsed_args, unparsed_args = arg_parser.parse_known_args(argv)
    argv = argv[:1] + unparsed_args

    logger = get_logger(parsed_args.debug)
    logger.info('Application starting')

    try:
        message_queue = mp.JoinableQueue()
        config = ConfigManager()

        if parsed_args.debug:
            logger.info('Running in DEBUG mode')
            config.set('run', 'debug_mode', 'True')

        dependencies = {
            "logger": logger,
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
        logger.info('Keyboard interrupt occurred, closing application')

        for proc in procs:
            proc.terminate()
            logger.info(f'Process terminated: {proc.name}')

def get_logger(debug_mode) -> Logger:
    logger = logging.getLogger(__name__)
    if debug_mode:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    info_handler = logging.StreamHandler()
    error_handler = logging.FileHandler('timelapse.log')

    info_handler.setLevel(logging.DEBUG)
    error_handler.setLevel(logging.ERROR)

    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    info_handler.setFormatter(log_format)
    error_handler.setFormatter(log_format)

    logger.addHandler(info_handler)
    logger.addHandler(error_handler)

    return logger