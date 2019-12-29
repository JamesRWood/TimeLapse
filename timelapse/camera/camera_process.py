import multiprocessing as mp
import os

from multiprocessing import JoinableQueue
from typing import Type
from datetime import datetime
from logging import Logger

from timelapse.config.config_manager import ConfigManager
from timelapse.messages import CaptureMessage
from timelapse.rpi.picamera_proxy import PiCameraProxy

class CameraProcess(mp.Process):
    def __init__(self, logger: Type[Logger], config: Type[ConfigManager], messageQueue: Type[JoinableQueue]):
        super().__init__()
        self._messageQueue = messageQueue
        self._logger = logger
        self._config = config
        self._camera = PiCameraProxy()

    def run(self, run_once=False):
        image_folder_path = self._config.get('run', 'image_folder')
        try:
            os.stat(image_folder_path)
        except:
            os.mkdir(image_folder_path)

        try:
            cont = True
            while cont:
                message = self._messageQueue.get()

                if isinstance(message, CaptureMessage):                    
                    self._camera.capture(os.path.join(image_folder_path, 'Img_' + self._get_timeStamp()))

                if run_once:
                    cont = False
            return
        except KeyboardInterrupt:
            return
        except:
            self._logger.exception('Exception occurred', exc_info=True)

    def _get_timeStamp(self) -> str:
        currentTime = datetime.now()
        return currentTime.strftime('%d-%m-%Y_%H:%M:%S:%f')