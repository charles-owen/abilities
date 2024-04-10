"""
Projector point projection test

Usage:
    projector-point --projector=<id> --point-f=<pt>

Options:
    --projector=<id>            Projector screen to use (starting at 1)
    --point-f=<pt>               Point to draw on the screen as fraction of x,y axis
"""

from docopt import docopt
from abilities import FullscreenShow
import cv2
import numpy as np

#
# Program entry point
#
if __name__ == '__main__':
    args = docopt(__doc__)
    print(args)

    fullscreen = FullscreenShow('projector', int(args['--projector']))
    fullscreen.open()

    wid = fullscreen.width
    hit = fullscreen.height
    image = np.ones((hit, wid), dtype=np.float32)

    p = args['--point-f'].split(',')
    x = int(wid * float(p[0]))
    y = int(hit * float(p[1]))

    size = 100
    size2 = int(size)
    cv2.line(image, (x-size2, y), (x+size2, y), (0, 0, 255))
    cv2.line(image, (x, y-size2), (x, y+size2), (0, 0, 255))

    fullscreen.imshow(image)

    cv2.waitKey()