"""
Example that demonstrates drawing a coordinate axis in
on the projector for projective AR

Usage:
    axis-only --screen=<screen> <calibration-file>

Options:
    --screen=<screen>       Specify the screen output to use for the projector
    <calibration-file>      The file to load with the calibration data in it
"""
import sys
import os

# Add the parent directory of the current script to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from docopt import docopt
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from p3dutil import Axis
from abilities import Calibration
from p3dutil import Projector
from panda3d.core import LVector3f
from panda3d.core import CardMaker, TextNode
from panda3d.core import LVector4


class MyApp(ShowBase):
    def __init__(self, args):
        ShowBase.__init__(self, windowType="none")

        self.calibration = Calibration()
        self.calibration.read(args['<calibration-file>'])

        projector = Projector()
        projector.open_fullscreen(self, args['--screen'])
        projector.set_projection(self, self.calibration, 1, 4)

        # This is drawing the Y axis negated, so it will come out towards the
        # camera rather than away from it into the back wall.
        self.axis = Axis(parent=self.render, size=0.5, axis=LVector3f(1, -1, 1))
        # cm = CardMaker('plane')
        # cm.setFrame(-2, 4, -2, 2) 
        # horizontal_plane = self.render.attachNewNode(cm.generate())
        # horizontal_plane.setPos(0, 0, -4)  
        # horizontal_plane.setHpr(0, -90, 0)
        # horizontal_plane.setColor(LVector4(0, 1, 0, 1))

#
# Program entry point
#
if __name__ == '__main__':
    args = docopt(__doc__)
    # print(args)

    app = MyApp(args)
    app.run()
