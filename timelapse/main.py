import argparse
import logging
import multiprocessing as mp
import logging.config
from os import path

from multiprocessing import JoinableQueue

from timelapse.config.config_manager import ConfigManager
from timelapse.timer.timer_process import TimerProcess
from timelapse.camera.camera_process import CameraProcess

def main(argv):
    log_file_path = path.join(path.dirname(path.abspath(__file__)), 'log.conf')
    logging.config.fileConfig(log_file_path, defaults={'logfilename': 'timelapse.log'}, disable_existing_loggers=False)

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--debug', action='store_true', help='run in debug mode')

    parsed_args, unparsed_args = arg_parser.parse_known_args(argv)
    argv = argv[:1] + unparsed_args

    logger = logging.getLogger(__name__)
    logger.info('Application starting')

    try:
        message_queue = mp.JoinableQueue()
        config = ConfigManager()

        if parsed_args.debug:
            logger.error('Running in DEBUG mode')
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
        logger.info('Keyboard interrupt occurred, closing application')

        for proc in procs:
            proc.terminate()
            logger.info(f'Process terminated: {proc.name}')