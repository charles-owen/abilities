"""
Example that demonstrates drawing a coordinate axis in
on the projector for projective AR

Usage:
    axis-only --screen=<screen> <calibration-file>

Options:
    --screen=<screen>       Specify the screen output to use for the projector
    <calibration-file>      The file to load with the calibration data in it
"""

from docopt import docopt
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from p3dutil import Axis
from abilities import Calibration
from p3dutil import Projector


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


#
# Program entry point
#
if __name__ == '__main__':
    args = docopt(__doc__)
    # print(args)

    app = MyApp(args)
    app.run()
