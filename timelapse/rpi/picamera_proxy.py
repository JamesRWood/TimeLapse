_picameraLoaded = True

try:
    from picamera import PiCamera
except:
    _picameraLoaded = False

class PiCameraProxy():
    def capture(self, filename: str):
        if _picameraLoaded:
            camera = PiCamera()
            camera.capture(filename)
            camera.close()
        print(filename)