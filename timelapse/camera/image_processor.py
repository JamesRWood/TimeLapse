import os, time, logging
import multiprocessing as mp

from multiprocessing import Process, Event

from datetime import datetime
from typing import Type

_pilLoaded = True

try:
    from PIL import Image
except:
    _pilLoaded = False

from timelapse.config_manager import ConfigManager
from timelapse.log_manager import LogManager
from timelapse.messages import ProcessImageMessage, KillProcessMessage

class ImageProcessor(Process):
    def __init__(self, img_c_pipe, caller):
        super(ImageProcessor, self).__init__()
        self._img_c_pipe = img_c_pipe
        self.caller = caller
        self._resolution = (ConfigManager.getInt('camera', 'resolution_width'), ConfigManager.getInt('camera', 'resolution_height'))
        pil_logger = logging.getLogger('PIL.PngImagePlugin')
        pil_logger.setLevel(logging.WARNING)

    def run(self):
        image_folder_path = ConfigManager.get('run', 'image_folder')
        try:
            os.stat(image_folder_path)
        except:
            os.mkdir(image_folder_path)
        
        run = True
        while run:
            message = self._img_c_pipe.recv()

            if isinstance(message, ProcessImageMessage):
                image_path = os.path.join(image_folder_path, 'Img_' + self._get_timeStamp()) + '.jpg'

                if _pilLoaded:

                    ## ---------------PNG shoot mode----------------
                    ## Interval must be >= 6s
                    # rawIO = message._image_stream
                    # rawIO.seek(0)
                    # img = Image.open(rawIO)
                    # rgb_img = img.convert('RGB')
                    # rgb_img.save(image_path, 'JPEG', quality=95)
                    ## ---------------------------------------------

                    ## ---------------JPEG shoot mode---------------
                    ## Interval must be >= 2s
                    rawIO = message._image_stream
                    rawIO.seek(0)
                    img = Image.open(rawIO)
                    img.save(image_path, 'JPEG', quality=95)
                    ## ---------------------------------------------

                    ## ---------------RGB shoot mode---------------
                    # img = Image.frombytes('RGB', self._resolution, message._image_stream)
                    # img.save(image_path, 'JPEG', quality=95)
                    ## ---------------------------------------------

                LogManager.log_debug(__name__, 'Processed: ' + image_path)

            elif isinstance(message, KillProcessMessage):
                LogManager.log_info(__name__, 'ImageProcess closing')
                self._img_c_pipe.close()
                run = False
        return

    def _get_timeStamp(self) -> str:
        currentTime = datetime.now()
        return currentTime.strftime('%d-%m-%Y_%H%M%S')