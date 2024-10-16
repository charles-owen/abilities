import sys
import os

# Add the parent directory of the current script to sys.path
sys.path.append(os.path.abspath(os.path.join(__file__, os.pardir, os.pardir, os.pardir)))

import unittest
from abilities import Calibration
import numpy as np
import math

class CalibrationTest(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self._dir = os.path.dirname(os.path.abspath(__file__))
        pass


    def test_read(self):
        calibration = Calibration()
        calibration.read(self._dir + "/data/calibration.yaml.dat")
        # print(calibration.imsize)
        self.assertTrue(
            np.allclose(calibration.imsize, [1080, 1920]),
                           msg="Image size read")

    def test_project(self):
        calibration = Calibration()
        calibration.read(self._dir + "/data/calibration.yaml.dat")

        u, v = calibration.project(0.01890533, 0.12916625, 0.00284014)
        # print(f"{u}, {v}")
        self.assertAlmostEqual(u, 385.8566745633289, 5)
        self.assertAlmostEqual(v, 699.1137169777264, 5)

        u, v = calibration.project(-0.05214326, -0.03002264, -0.00936422)
        # print(f"{u}, {v}")
        self.assertAlmostEqual(u, 122.20530471183292, 5)
        self.assertAlmostEqual(v, 113.11239784085149, 5)

    def test_project2d(self):
        calibration = Calibration()
        calibration.read(self._dir + "/data/calibration2d.yaml.dat")

        u, v = calibration.project2d(0.0, 0.0)
        # print(f"{u}, {v}")
        self.assertAlmostEqual(u, 1288.2850493736892, 5)
        self.assertAlmostEqual(v, 345.4729947954919, 5)

    def test_unproject2d(self):
        calibration = Calibration()
        calibration.read(self._dir + "/data/calibration2d.yaml.dat")

        x, y = calibration.unproject2d(1288.2850493736892, 345.4729947954919)
        # print(f"{x}, {y}")

        self.assertAlmostEqual(x, 0, 5)
        self.assertAlmostEqual(y, 0, 5)

        for x0, x1 in [(112, 78), (-182.7, -53.1)]:
            u, v = calibration.project2d(x0, x1)
            x, y = calibration.unproject2d(u, v)

            self.assertAlmostEqual(x, x0, 5)
            self.assertAlmostEqual(y, x1, 5)

    def test_unproject(self):
        calibration = Calibration()
        calibration.read(self._dir + "/data/calibration.yaml.dat")

        o, d = calibration.unproject(385.8566745633289, 699.1137169777264)
        p = calibration.ray_intersect_xy(o, d, 0.00284014)
        self.assertAlmostEqual(p[0][0], 0.01890533, 5)
        self.assertAlmostEqual(p[1][0], 0.12916625, 5)
        self.assertAlmostEqual(p[2][0], 0.00284014, 5)

        o, d = calibration.unproject(122.20530471183292, 113.11239784085149)
        p = calibration.ray_intersect_xy(o, d, -0.00936422)
        self.assertAlmostEqual(p[0][0], -0.05214326, 5)
        self.assertAlmostEqual(p[1][0], -0.03002264, 5)
        self.assertAlmostEqual(p[2][0], -0.00936422, 5)

    def test_angle(self):
        calibration = Calibration()
        calibration.read(self._dir + "/data/calibration-lab.yaml.dat")

        o1, d1 = calibration.unproject(0.0, 768.0/2)
        o2, d2 = calibration.unproject(1024.0, 768.0/2)

        dot = d1[0][0] * d2[0][0] + d1[1][0] * d2[1][0] + d1[2][0] * d2[2][0];
        angle = math.degrees(math.acos(dot))

        # print(d1)
        # print(d2)
        # print(angle)

        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
