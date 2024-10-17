"""
General purpose streaming script

This will stream from a camera or from a movie file. This serves as
a test for the classes Streamer and StreamerCommandLine

This will work for both OpenCV VideoCamera devices and for Pylon cameras. By default, it will
select the first available Pylon camera. If that does not exist or if Pylon is not available,
it selects the first available OpenCV VideoCapture camera.

Choose --camera=1 will force the first VideoCapture camera. Choosing --camera=p1 will force
the first Pylon camera.

Press ESC or q to close the window and exit. + increase zoom, - decreases zoom

Usage:
    camera-stream [--camera=<id>] [--movie=<movie>] [--config=<config>]

Options:
    --camera=<id>           Camera number to use - starting at 1. Prefix with 'p' to force Pylon camera
    --movie=<movie>         Movie to play rather than the camera
    --config=<config>       Config file to use that specifies the parameters
"""

import sys
import os

# Add the parent directory of the current script to sys.path
sys.path.append(os.path.abspath(os.path.join(__file__, os.pardir, os.pardir, os.pardir)))

from docopt import docopt
import cv2
from abilities import Streamer

class StreamerConcrete(Streamer):
    """
    Simple example of how to use StreamerCommandLine to stream video
    from a camera or file.
    """
    def __init__(self, docopt_args):
        super().__init__(docopt_args)

        self._zoom = 1.0

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
