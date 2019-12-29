_picameraLoaded = True

try:
    from picamera import PiCamera
    _camera = PiCamera()
except:
    _picameraLoaded = False

class PiCameraProxy():
    def capture(self, filename: str):
        if _picameraLoaded:
            _camera.capture(filename)
        else:
            print(filename)