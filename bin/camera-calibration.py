"""
Camera calibration script

Usage:
    camera-calibration --camera=<id> [--show] [--write=<filename>] [--projector=<id>] [--invert] [--offset=<offset>]
    camera-calibration --files=<description> [--show] [--delay=<delay>] [--write=<filename>] [--offset=<offset>]

Options:
    --camera=<id>               Camera number to use
    --show                      Display frames used for calibration
    --write <filename>          Write calibration to a file
    --files=<description>       Calibrate from files based on description file (XML)
    --delay=<delay>             Delay in seconds after each frame is shown [default: 1.0]
    --projector=<id>            Optional projector screen to set to white output (starting at 1)
    --invert                    If set, invert the camera image (display only)
    --offset=<offset>           Offset to add to the camera calibration
"""

from docopt import docopt
from abilities import CameraCalibration
from abilities import FullscreenShow

#
# Program entry point
#
if __name__ == '__main__':
    args = docopt(__doc__)
    # print(args)

    calibration = CameraCalibration()
    calibration.args(args)

    if calibration.compute():
        print("Calibration computed successfully")

