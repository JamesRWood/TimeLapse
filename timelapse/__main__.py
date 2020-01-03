import sys
import timelapse
# import logging.config
# from os import path

# log_file_path = path.join(path.dirname(path.abspath(__file__)), 'log.conf')
# logging.config.fileConfig(log_file_path, defaults={'logfilename': 'timelapse.log'}, disable_existing_loggers=False)

sys.exit(timelapse.main(sys.argv))