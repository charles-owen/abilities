from abc import ABC, abstractmethod
import cv2

from .generalcamera import GeneralCamera
from .exceptions import OpenFailedException
from .streamerconfig import StreamerConfig

class Streamer(ABC):
    """
    Base class for classes that need to stream content from either
    a live camera or movie file. Meant to simplify applications that
    need to read from a file for development, then be subject to
    deployment with a live camera.
    """

    def __init__(self, docopt_args):
        if '--config' in docopt_args and docopt_args['--config'] is not None:
            self._config = StreamerConfig(docopt_args, docopt_args['--config'])
        else:
            self._config = StreamerConfig(docopt_args, None)

        self._frame_number = 0

    def start(self):
        self.on_start()

        device = None
        config = self._config

        if config.camera is not None:
            device = GeneralCamera(gain=0, frame_rate=30, camera=config.camera)
            if not device.open():
                raise OpenFailedException(f"Unable to open camera {config.camera}")

        elif config.movie is not None:
            device = cv2.VideoCapture(config.movie)
            if not device.isOpened():
                raise OpenFailedException(f"Unable to open movie {config.movie}")

        if device is not None:
            while True:
                ret, frame = device.read()
                if not ret:
                    break

                self._frame_number += 1

                self.on_frame(frame)
                key = cv2.waitKey(1) & 0xff
                if not self.on_key(key, frame):
                    if key == ord('q') or key == 27:
                        break

        self.on_stop()

    def on_start(self):
        pass

    def on_stop(self):
        pass

    @abstractmethod
    def on_frame(self, frame):
        pass

    def on_key(self, key, frame):
        return False

    @property
    def config(self):
        return self._config

    @property
    def camera(self):
        return self._config.camera

    @property
    def movie(self):
        return self._config.movie

    @property
    def frame_number(self):
        return self._frame_number