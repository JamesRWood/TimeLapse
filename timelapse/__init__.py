import sys
from .main import main
# import logging.config
# from os import path

if __name__ == "__main__":
    # log_file_path = path.join(path.dirname(path.abspath(__file__)), 'log.conf')
    # logging.config.fileConfig(log_file_path, defaults={'logfilename': 'timelapse.log'}, disable_existing_loggers=False)

    sys.exit(main(sys.argv))