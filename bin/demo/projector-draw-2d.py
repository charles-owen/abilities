"""
Demonstration of how to draw on the projector assuming a 2D calibration

Usage:
    projector-draw-2d --projector=<id> <calibration-file>

Options:
    --projector=<id>            Projector screen to use (starting at 1)
    <calibration-file>          The file to load with the projector calibration data in it
"""
import sys
import os

# Add the parent-parent directory of the current script to sys.path
sys.path.append(os.path.abspath(os.path.join(__file__, os.pardir, os.pardir, os.pardir, os.pardir)))

from docopt import docopt
from abilities import Calibration
from abilities import FullscreenShow
import cv2
import numpy as np

#
# Program entry point
#
if __name__ == '__main__':
    args = docopt(__doc__)
    #print(args)

    # This creates a calibration object and loads
    # the projector calibration into it
    projector_calibration = Calibration()
    projector_calibration.read(args['<calibration-file>'])

    # This opens a full-screen window on the projector screen that we can show images in
    fullscreen = FullscreenShow('projector', int(args['--projector']))
    fullscreen.open()

    # This creates a white image we can draw on and project
    # Change to zeros to draw black, of ocurse
    wid = fullscreen.width
    hit = fullscreen.height
    image = np.ones((hit, wid), dtype=np.float32)

    # Convert two world coordinates to image coordinates using the projector calibration
    # and draw a line between them
    u1, v1 = projector_calibration.project2d(0, 0)
    u2, v2 = projector_calibration.project2d(0.30, 0.20)
    cv2.line(image, (int(u1), int(v1)), (int(u2), int(v2)), (0, 0, 255))

    # Show the image
    fullscreen.imshow(image)

    cv2.waitKey()