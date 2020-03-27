import time, io, os

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

from multiprocessing import Process, Event, JoinableQueue
from typing import Type
from datetime import datetime

from timelapse.config_manager import ConfigManager
from timelapse.messages import CaptureMessage, ProcessImageMessage, KillProcessMessage
from timelapse.log_manager import LogManager

class CameraProcess(Process):
    def __init__(self, timer_queue: Type[JoinableQueue], caller):
        super(CameraProcess, self).__init__()
        self._timer_queue = timer_queue
        self.caller = caller

    def run(self):
        run = True        
        cam = self._get_cam()
        stream = io.BytesIO()

        image_folder_path = ConfigManager.get('run', 'image_folder')
        try:
            os.stat(image_folder_path)
        except:
            os.mkdir(image_folder_path)

        while run:
            message = self._timer_queue.get()
            
            if isinstance(message, CaptureMessage):                
                try:
                    cam.capture(stream, format='jpeg', quality=95)
                    stream.seek(0)

                    image_path = os.path.join(image_folder_path, 'Img_' + self._get_timeStamp()) + '.jpg'
                    if _pilLoaded and _picamera_loaded:
                        img = Image.open(stream)                        
                        img.save(image_path, 'JPEG', quality=95)

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
            resolution = (ConfigManager.getInt('camera', 'resolution_width'), ConfigManager.getInt('camera', 'resolution_height'))
            framerate = ConfigManager.getInt('camera', 'framerate')
            rotation = ConfigManager.getInt('camera', 'rotation')
            cam =  PiCamera(resolution=resolution, framerate=framerate)
            cam.rotation = rotation
            time.sleep(2)   # Allow PiCamera necessary time to auto-adjust settings
            return cam
        else:
            return DummyCam()

    def _get_timeStamp(self) -> str:
        currentTime = datetime.now()
        return currentTime.strftime('%d-%m-%Y_%H%M%S')

class DummyCam():
    def capture(self, stream, format, quality):
        pass

    def close(self):
        pass