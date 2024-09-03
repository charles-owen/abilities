from abc import ABC, abstractmethod
import cv2

from .generalcamera import GeneralCamera
from .exceptions import OpenFailedException


class Streamer(ABC):
    """
    Base class for classes that need to stream content from either
    a live camera or movie file. Meant to simplify applications that
    need to read from a file for development, then be subject to
    deployment with a live camera.

    There are two derived versions:

    StreamerCommandLine - Expects the camera or movie be specified using command line arguments
    StreamerConfig - Expects the camera or movie be specified using a JSON config file
    """

    def __init__(self):
        # Camera to use if camera option selected
        self._camera = None

        # Movie to use if movie option selected
        self._movie = None

    def set_camera(self, camera):
        self._camera = GeneralCamera(gain=0, frame_rate=30, camera=camera)
        if not self._camera.open():
            raise OpenFailedException(f"Unable to open camera {camera}")

    def set_movie(self, movie):
        self._movie = cv2.VideoCapture(movie)
        if not self._movie.isOpened():
            raise OpenFailedException(f"Unable to open movie {movie}")

    def start(self):
        self.on_start()

        device_to_use = None

        if self._camera is not None:
            device_to_use = self._camera
        elif self._movie is not None:
            device_to_use = self._movie

        if device_to_use is not None:
            while True:
                ret, frame = device_to_use.read()

                self.on_frame(frame)
                key = cv2.waitKey(1) & 0xff
                if not self.on_key(key):
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

    def on_key(self, key):
        return False


