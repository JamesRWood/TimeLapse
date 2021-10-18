import io
import os
import time

from datetime import datetime
from multiprocessing import Process

from timelapse.json_config_manager import JsonConfigManager
from timelapse.log_manager import LogManager
from timelapse.messages import CaptureMessage, KillProcessMessage

_picamera_loaded = True
_pilLoaded = True

try:
    import picamera.array
    from picamera import PiCamera
except:
    _picamera_loaded = False

try:
    from PIL import Image
except:
    _pilLoaded = False


class CameraProcess(Process):
    def __init__(self, timer_queue, caller, config: JsonConfigManager):
        super(CameraProcess, self).__init__()
        self._timer_queue = timer_queue
        self.caller = caller
        self._config = config

    def run(self):
        self._run_configuration = self._config.run_configuration
        self._camera_configuration = self._config.camera_configuration
        run = True
        cam = self._get_cam()
        stream = io.BytesIO()

        try:
            os.stat(self._run_configuration.image_folder)
        except:
            os.mkdir(self._run_configuration.image_folder)

        while run:
            message = self._timer_queue.get()

            if isinstance(message, CaptureMessage):
                try:
                    cam.capture(stream, format='jpeg', quality=95)

                    image_path = os.path.join(self._run_configuration.image_folder, 'Img_' + self._get_time_stamp()) + '.jpg'
                    if _pilLoaded and _picamera_loaded:
                        raw_io = stream
                        raw_io.seek(0)
                        img = Image.open(raw_io)
                        img.save(image_path, 'JPEG', quality=95)

                    stream.seek(0)
                    stream.truncate()
                    LogManager.log_debug(__name__, 'Processed: ' + image_path)

                except Exception as e:
                    LogManager.log_error(__name__, f'{e}')

                self._timer_queue.task_done()

            elif isinstance(message, KillProcessMessage):
                LogManager.log_info(__name__, 'CameraProcess closing')
                self._timer_queue.task_done()
                self._timer_queue.close()
                stream.close()
                cam.close()
                run = False
        return

    def _get_cam(self):
        if _picamera_loaded:
            resolution = (self._camera_configuration.resolution_width, self._camera_configuration.resolution_height)
            framerate = self._camera_configuration.framerate
            rotation = self._camera_configuration.rotation
            cam = PiCamera(resolution=resolution, framerate=framerate)
            cam.rotation = rotation
            time.sleep(2)   # Allow PiCamera necessary time to auto-adjust settings
            return cam
        else:
            return DummyCam()

    @staticmethod
    def _get_time_stamp() -> str:
        current_time = datetime.now()
        return current_time.strftime('%d-%m-%Y_%H%M%S')


class DummyCam:
    def capture(self, stream, format, quality):
        pass

    def close(self):
        pass
