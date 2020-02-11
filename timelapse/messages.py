from typing import Type

class CaptureMessage():
    def __init__(self):
        self

class ProcessImageMessage():
    def __init__(self, image_stream):
        self._image_stream = image_stream

class KillProcessMessage():
    def __init__(self):
        self