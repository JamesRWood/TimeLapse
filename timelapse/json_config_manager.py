import json
import os
import typing
from datetime import datetime


class RunSchedule(object):
    def __init__(self, start, end):
        self.start = datetime.strptime(start, '%d/%m/%Y_%H:%M:%S')
        self.end = datetime.strptime(end, '%d/%m/%Y_%H:%M:%S')


def build_schedule_array(schedules_dict) -> typing.List[RunSchedule]:
    schedule_list = []
    for i in range(len(schedules_dict)):
        schedule_list.append(RunSchedule(schedules_dict[i]['start'], schedules_dict[i]['end']))

    return schedule_list


class RunConfiguration(object):
    def __init__(self, debug_mode, image_folder, interval, schedules):
        self.debug_mode = debug_mode == 'true'
        self.image_folder = image_folder
        self.interval = int(interval)
        self.schedules = build_schedule_array(schedules)


class CameraConfiguration(object):
    def __init__(self, resolution_width, resolution_height, framerate, rotation):
        self.resolution_width = int(resolution_width)
        self.resolution_height = int(resolution_height)
        self.framerate = int(framerate)
        self.rotation = int(rotation)


class JsonConfigManager(object):
    def __init__(self):
        filename = os.path.join(os.path.dirname(__file__), 'run_configuration.json')
        with open(filename) as f:
            data = json.load(f)
            self.run_configuration = RunConfiguration(
                data['run_configuration']['debug_mode'],
                data['run_configuration']['image_folder'],
                data['run_configuration']['interval'],
                data['run_configuration']['schedules'])
            self.camera_configuration = CameraConfiguration(
                data['camera_configuration']['resolution_width'],
                data['camera_configuration']['resolution_height'],
                data['camera_configuration']['framerate'],
                data['camera_configuration']['rotation'])
