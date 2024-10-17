"""
Marker tracking demonstration script

Press ESC or q to close the window and exit. + increase zoom, - decreases zoom

Usage:
    marker-tracking [--camera=<id>] [--movie=<movie>] [--config=<config>] --calibration=<calibration>

Options:
    --camera=<id>           Camera number to use - starting at 1. Prefix with 'p' to force Pylon camera
    --movie=<movie>         Movie to play rather than the camera
    --config=<config>       Config file to use that specifies the parameters
    --calibration=<calibration> Calibration file to use
"""

import sys
import os

# Add the parent directory of the current script to sys.path
sys.path.append(os.path.abspath(os.path.join(__file__, os.pardir, os.pardir, os.pardir, os.pardir)))

from docopt import docopt
import cv2
import numpy as np
from abilities import Streamer
from abilities import Calibration

class StreamerConcrete(Streamer):
    """
    Simple example of how to use StreamerCommandLine to stream video
    from a camera or file.
    """
    def __init__(self, docopt_args):
        super().__init__(docopt_args)

        self._zoom = 1.0

        self._calibration = Calibration()
        self._calibration.read(docopt_args['--calibration'])

        self._marker_size = 0.060
        dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self._dictionary = dictionary
        detection_params = cv2.aruco.DetectorParameters()
        self._detector = cv2.aruco.ArucoDetector(dictionary, detection_params)

    def on_start(self):
        """
        Called when streaming starts.
        """
        cv2.namedWindow("Video Stream", cv2.WINDOW_AUTOSIZE)
        cv2.startWindowThread()

    def on_frame(self, frame):
        """
        Called for each new frame.
        :param frame: The OpenCV frame
        """

        marker_corners, marker_ids, rejected_candidates = self._detector.detectMarkers(frame)
        cv2.aruco.drawDetectedMarkers(frame, marker_corners, marker_ids, (255, 0, 0))

        marker_length = self._marker_size
        obj_points = np.array([[0, 0, 0], [marker_length, 0, 0], [marker_length, marker_length, 0], [0, marker_length, 0]])

        for i in range(0, len(marker_corners)):
            retval, rvec, tvec = cv2.solvePnP(obj_points, marker_corners[i], self._calibration.mtx, self._calibration.dist)
            cv2.drawFrameAxes(frame, self._calibration.mtx, self._calibration.dist, rvec, tvec, marker_length)

        if self._zoom != 1.0:
            frame = cv2.resize(frame, (0, 0), fx=self._zoom, fy=self._zoom)

        cv2.imshow('Video Stream', frame)

    def on_stop(self):
        """
        Called when streaming stops, either by the user or end of stream
        :return:
        """
        cv2.destroyWindow("Video Stream")

    def on_key(self, key, frame):
        """
        Called when a key is pressed by the user.
        :param key: Key that is pressed
        :return: True if key is handled, otherwise False
        """
        if key == ord('-'):
            self._zoom /= 2
            return True

        if key == ord('+'):
            self._zoom *= 2
            return True

        return False


#
# Program entry point
#
if __name__ == '__main__':
    args = docopt(__doc__)
    print(args)

    streamer = StreamerConcrete(args)
    streamer.start()
