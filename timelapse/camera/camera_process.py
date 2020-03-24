import time, io

_picamera_loaded = True

try:
    import picamera.array
    from picamera import PiCamera
except:
    _picamera_loaded = False

from multiprocessing import Process, Event
from typing import Type

from timelapse.config_manager import ConfigManager
from timelapse.messages import CaptureMessage, ProcessImageMessage, KillProcessMessage
from timelapse.log_manager import LogManager

class CameraProcess(Process):
    def __init__(self, timer_c_pipe, img_p_pipe, caller):
        super(CameraProcess, self).__init__()
        self._timer_c_pipe = timer_c_pipe
        self._img_p_pipe = img_p_pipe        
        self.caller = caller

    def run(self):
        run = True        
        cam = self._get_cam()
        stream = picamera.array.PiRGBArray(cam)

        while run:
            message = self._timer_c_pipe.recv()
            
            if isinstance(message, CaptureMessage):                
                try:
                    cam.capture(stream, format='rgb')
                    self._img_p_pipe.send(ProcessImageMessage(stream.array))                    
                    stream.seek(0)
                    stream.truncate()
                except Exception as e:
                    LogManager.log_error(__name__, f'{e}')

            elif isinstance(message, KillProcessMessage):
                LogManager.log_info(__name__, 'CameraProcess closing')
                self._timer_c_pipe.close()
                stream.close()
                cam.close()
                self._img_p_pipe.send(KillProcessMessage())
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

class DummyCam():
    def capture(self, stream, format, quality):
        pass

    def close(self):
        pass
