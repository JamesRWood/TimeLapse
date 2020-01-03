import os, logging
from logging import Logger

class LogManager(object):
    logging.config.fileConfig(os.path.join(os.path.dirname(__file__), 'log.cfg'), defaults={'logfilename': 'timelapse.log'}, disable_existing_loggers=False)

    logger_dict = {}

    @staticmethod
    def log_debug(name: str, message: str):
        logger_instance = LogManager._get_logger(name)
        logger_instance.debug(message)

    @staticmethod
    def log_info(name: str, message: str):        
        logger_instance = LogManager._get_logger(name)
        logger_instance.info(message)

    @staticmethod
    def log_warning(name: str, message: str):
        logger_instance = LogManager._get_logger(name)
        logger_instance.warning(message)

    @staticmethod
    def log_error(name: str, message: str):
        logger_instance = LogManager._get_logger(name)
        logger_instance.error(message)

    @staticmethod
    def log_critical(name: str, message: str):
        logger_instance = LogManager._get_logger(name)
        logger_instance.critical(message)

    @staticmethod
    def _get_logger(name: str):
        if name in LogManager.logger_dict.keys():
            return LogManager.logger_dict[name]
        else:
            l = logging.getLogger(name)
            LogManager.logger_dict[name] = l
            return l