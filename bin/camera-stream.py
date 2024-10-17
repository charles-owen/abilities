"""
Camera streaming script

This will work for both OpenCV VideoCamera devices and for Pylon cameras. By default, it will
select the first available Pylon camera. If that does not exist or if Pylon is not available,
it selects the first available OpenCV VideoCapture camera.

Choose --camera=1 will force the first VideoCapture camera. Choosing --camera=p1 will force
the first Pylon camera.

Press ESC or q to close the window and exit.

Usage:
    camera-stream [--camera=<id>] [--projector=<id>]

Options:
    --camera=<id>           Camera number to use - starting at 1. Prefix with 'p' to force Pylon camera
    --projector=<id>        Optional projector screen to set to white output (starting at 1)
"""

import sys
import os

# Add the parent directory of the current script to sys.path
sys.path.append(os.path.abspath(os.path.join(__file__, os.pardir, os.pardir, os.pardir)))

from docopt import docopt
from abilities import GeneralCamera
from abilities import FullscreenShow
import cv2


def stream(docopt_args):

    fullscreen = None

    if docopt_args['--projector']:
        fullscreen = FullscreenShow('projector', int(docopt_args['--projector']))
        fullscreen.open()
        fullscreen.white()

    # Options that can be passed to the constructor
    # height=2160
    # width=3840
    # prefer_pylon=False (default=True)
    #
    # Pylon-only features:
    # gain = 0 (Pylon only)
    # exposure_time=30000 (microseconds, Pylon only)
    # frame_rate = 30 (Pylon only)

    camera = GeneralCamera(gain=0, frame_rate=30, camera=docopt_args['--camera'])
    if not camera.open():
        print("Unable to open camera")
        return 1

    wid = camera.width
    hit = camera.height
    has_p = camera.has_pylon
    fps = camera.frame_rate
    print(f'{wid} {hit} {has_p} {fps}')

    cv2.namedWindow("Camera Stream", cv2.WINDOW_AUTOSIZE)
    cv2.startWindowThread()

    zoom = 1.0

    while True:
        ret, frame = camera.read()

        # height, width, channels = frame.shape
        # print(f"{width} {height} {channels}")

        if zoom != 1.0:
            frame = cv2.resize(frame, (0, 0), fx=zoom, fy=zoom)

        cv2.imshow('frame', frame)
        key = cv2.waitKey(1) & 0xff

        if key == ord('-'):
            zoom /= 2

        if key == ord('+'):
            zoom *= 2

        if key == ord('q') or key == 27:
            break

    cv2.destroyAllWindows()


#
# Program entry point
#
if __name__ == '__main__':
    args = docopt(__doc__)
    # print(args)

    stream(args)
