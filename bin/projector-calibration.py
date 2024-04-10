"""
Projector calibration script

Usage:
    projector-calibration <config-file>

Options:
    <config-file>           YAML configuration file
"""

# Usage:
#     projector-calibration [--screen=<screen>] [--camera=<id>] [--omit=<omit>]  [--write=<filename>] [--invert] --camera-calibration=<file>
#
# Options:
#     --camera=<id>               Camera to use
#     --screen=<screen>           Screen number to display on
#     --omit=<omit>               Comma delimited list of marker to omit
#     --camera-calibration=<file> Camera calibration file to use
#     --write <filename>          Write calibration to a file
#     --invert                    If set, invert the camera image

from docopt import docopt
from abilities import ProjectorCalibration


if __name__ == '__main__':
    args = docopt(__doc__)
    # print(args)

    calibration = ProjectorCalibration()
    calibration.args(args)

    calibration.calibrate()
