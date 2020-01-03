from typing import Type

from timelapse.camera.capture_mode import CaptureMode

class CaptureMessage():
    def __init__(self, capture_mode: Type[CaptureMode]):
        self._capture_mode: CaptureMode = capture_mode

    def CaptureMode(self) -> CaptureMode:
        return self._capture_mode

class RunCompleteMessage():
    pass