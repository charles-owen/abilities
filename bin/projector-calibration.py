"""
Projector calibration script

Usage:
    projector-calibration <config-file>

Options:
    <config-file>           YAML configuration file
"""


import sys
import os

# Add the parent directory of the current script to sys.path
sys.path.append(os.path.abspath(os.path.join(__file__, os.pardir, os.pardir, os.pardir)))

from docopt import docopt
from abilities import ProjectorCalibration


if __name__ == '__main__':
    args = docopt(__doc__)
    # print(args)

    calibration = ProjectorCalibration()
    calibration.args(args)

    calibration.calibrate()
