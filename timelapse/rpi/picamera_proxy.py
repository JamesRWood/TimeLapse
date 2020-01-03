_picamera_loaded = True

try:
    from picamera import PiCamera
except:
    _picamera_loaded = False

import time

from typing import Type

from timelapse.log_manager import LogManager
from timelapse.config.config_manager import ConfigManager

class PiCameraProxy():
    def __init__(self, config: Type[ConfigManager]):
        self._camera_initialised = False
        if _picamera_loaded:
            self._camera = PiCamera(resolution=(config.getInt('camera', 'resolution_width'), config.getInt('camera', 'resolution_height')), framerate=config.getInt('camera', 'framerate'))
            self._camera.iso = config.getInt('camera', 'iso')
            time.sleep(2) # Wait for automatic gain control to settle
            self._camera.shutter_speed = self._camera.exposure_speed
            self._camera.exposure_mode = 'off'
            g = self._camera.awb_gains
            self._camera.awb_mode = 'off'
            self._camera.awb_gains = g
            self._camera_initialised = True

    def capture(self, filename: str):
        if _picamera_loaded:
            if self._camera_initialised:
                self._camera.capture(filename)
            else:
                time.sleep(0.5)
                self.capture(filename)
        LogManager.log_info(__name__, 'Capture: ' + filename)

    def dispose(self):
        if _picamera_loaded and self._camera_initialised:
            self._camera.close()