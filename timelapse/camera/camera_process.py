import multiprocessing as mp
import os

from multiprocessing import JoinableQueue
from typing import Type
from datetime import datetime

from timelapse.log_manager import LogManager
from timelapse.config.config_manager import ConfigManager
from timelapse.messages import CaptureMessage, RunCompleteMessage
from timelapse.rpi.picamera_proxy import PiCameraProxy

class CameraProcess(mp.Process):
    def __init__(self, config: Type[ConfigManager], messageQueue: Type[JoinableQueue]):
        super().__init__()

        self._messageQueue = messageQueue
        self._config = config
        self._camera = PiCameraProxy(config)

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
                    image_path = os.path.join(image_folder_path, 'Img_' + self._get_timeStamp()) + '.jpg'
                    self._camera.capture(image_path)

                if isinstance(message, RunCompleteMessage):
                    self._camera.dispose()

                if run_once:
                    cont = False
            return
        except KeyboardInterrupt:
            return

    def _get_timeStamp(self) -> str:
        currentTime = datetime.now()
        return currentTime.strftime('%d-%m-%Y_%H%M%S')