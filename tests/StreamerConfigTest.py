import sys
import os

# Add the parent directory of the current script to sys.path
sys.path.append(os.path.abspath(os.path.join(__file__, os.pardir, os.pardir, os.pardir)))

import unittest
from abilities import StreamerConfig

class StreamerConfigTest(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self._dir = os.path.dirname(os.path.abspath(__file__))
        pass

    def test_read(self):
        config = StreamerConfig({}, self._dir + "/data/config1.json")
        expected = {'camera-calibration': 'trial1.yaml', 'movie': 'trial1.mp4', 'zoom': 0.5, 'region': {'y-range-fm-mm': -15, 'y-range-to-mm': 5, 'x-range-fm-mm': -30, 'x-range-to-mm': -7}, 'background': {'sample': [120]}}
        self.assertDictEqual(expected, config.config)

    def test_include(self):
        config = StreamerConfig({}, self._dir + "/data/config2.json")
        expected = {'camera-calibration': 'trial1.yaml', 'movie': 'trial1.mp4', 'region': {'a': 7, 'y-range-fm-mm': -15, 'y-range-to-mm': 5, 'x-range-fm-mm': -30, 'x-range-to-mm': -7}, 'background': {'sample': [120]}, 'zoom': 0.5}
        self.assertDictEqual(expected, config.config)
