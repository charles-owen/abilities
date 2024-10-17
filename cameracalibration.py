from calibration import Calibration
from generalcamera import GeneralCamera
from fullscreenshow import FullscreenShow
import cv2
import os
import numpy as np

import xml.etree.ElementTree as et

class CameraCalibration(Calibration):

    def __init__(self):
        super().__init__()

        self._show = False
        self._delay = 0

        self._allCorners = []
        self._allIds = []
        self._allObjectPoints = []
        self._allImagePoints = []

        self._dictionary = None
        self._board = None
        self._detector = None
        self._zoom = 1.0
        self._invert = False
        self._write = None
        self._fullscreen = None
        self._offset = [0, 0, 0]
        return

    def args(self, args, ignore=None):
        """
        Provide docopt arguments to the component.
        :param args: docopt arguments dictionary
        :param ignore: Optional list of arguments that are to be ignored if present
        :return:
        """
        if ignore is None:
            ignore = []

        if '--projector' not in ignore and args['--projector']:
            self._fullscreen = FullscreenShow('projector', int(args['--projector']))
            self._fullscreen.open()
            self._fullscreen.white()

        if '--write' not in ignore and args['--write']:
            self._write = args['--write']

        if '--show' not in ignore and args['--show']:
            self._show = True

        if '--delay' not in ignore and args['--delay']:
            self._delay = float(args['--delay'])

        if '--invert' not in ignore and args['--invert']:
            self._invert = args['--invert']

        if '--offset' not in ignore and args['--offset']:
            o = args['--offset'].split(',')
            if len(o) < 3:
                print(f'--offset of {args["--offset"]} is invalid, must have three values in millimeters')
                return False
            self._offset = [float(o[0]) * 0.001, float(o[1]) * 0.001, float(o[2]) * 0.001]

        """
        These two must be last!
        """
        if '--camera' not in ignore and args['--camera']:
            self.initializeForCalibration()
            self.cameraCalibrate(args['--camera'])

        elif '--files' not in ignore and args['--files']:
            self.initializeForCalibration()
            self.filesCalibrate(args['--files'])

        return True

    def initializeForCalibration(self):
        self._allCorners = []
        self._allIds = []
        self._allObjectPoints = []
        self._allImagePoints = []

        self._dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_250)
        self._board = cv2.aruco.CharucoBoard((10, 8), 0.025, 0.019, self._dictionary)
        self._board.setLegacyPattern(True)
        self._detector = cv2.aruco.CharucoDetector(self._board)

    def frame(self, frame, take=True):
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.imsize = gray.shape

        # Detect the board
        corners, ids, markerCorners, markerIds = self._detector.detectBoard(gray)

        if self._show:
            frame2 = frame.copy()

            if self.valid:
                cc = self
                cv2.drawFrameAxes(frame2, cc.mtx, cc.distortion, cc.last_rvec, cc.last_tvec, 0.2)

            cv2.aruco.drawDetectedMarkers(frame2, markerCorners, markerIds, (255, 0, 0))

            if self._invert:
                frame2 = cv2.rotate(frame2, cv2.ROTATE_180)

            if self._zoom == 1.0:
                cv2.imshow('frame', frame2)
            else:
                frame2 = cv2.resize(frame2, (0, 0), fx=self._zoom, fy=self._zoom)
                cv2.imshow('frame', frame2)

        if corners is None:
            return

        if take and len(corners) > 0:
            if len(ids) >= 4:
                objectPoints, imagePoints = self._board.matchImagePoints(corners, ids)

                # Optional offset of the object points, so they can be relative to
                # a corner of the card rather than the first marker
                objectPoints2 = []
                for o in objectPoints:
                    o = [o[0] + self._offset]
                    objectPoints2.append(o)

                objectPoints2 = np.array(objectPoints2, dtype=np.float32)

                self._allCorners.append(corners)
                self._allIds.append(ids)
                self._allObjectPoints.append(objectPoints2)
                self._allImagePoints.append(imagePoints)
                print('{} ids {} captures'.format(len(ids), len(self._allCorners)))
                if len(self._allCorners) > 4:
                    self._compute()
            else:
                print('Insufficient captured ids (< 4)')

    def _compute(self):
        try:
            ret, self.mtx, self.dist, self.rvecs, self.tvecs = cv2.calibrateCamera(self._allObjectPoints, self._allImagePoints, self.imsize, None, None)

            if not ret:
                print(f'Calibration failed - false return value')
                return False

        except Exception as err:
            print(f'Calibration failed: {err}')
            return False

        self._valid = True
        return True

    def compute(self):
        """
        Compute a camera calibration based on collected Charuco frames
        :return: True if successful
        """
        # Calibration fails for lots of reasons.
        if not self._compute():
            return False

        if self._write is not None:
            self.write(self._write)

        return True

    def cameraCalibrate(self, id):
        camera = GeneralCamera(camera=id)
        if not camera.open():
            print("Unable to open camera")
            return False

        # # Start capturing images for calibration
        # cap = cv2.VideoCapture(int(id))

        while True:
            # Get a camera frame
            ret, frame = camera.read()
            if not ret:
                continue

            self.frame(frame, take=False)

            key = cv2.waitKey(1) & 0xff
            if key == ord('q') or key == 27:
                break
            elif key == ord(' ') or key == 3:   # 3 = right arrow key
                self.frame(frame, take=True)
            elif key == ord('-'):
                self._zoom /= 2
            elif key == ord('+'):
                self._zoom *= 2

        camera.close()
        cv2.destroyAllWindows()
        return True

    def filesCalibrate(self, descriptionFile):
        tree = et.parse(descriptionFile)
        root = tree.getroot()

        dir = os.path.dirname(descriptionFile)

        for file in root:
            filePath = dir + "/" + file.text
            print(filePath)

            cap = cv2.VideoCapture(filePath)
            ret, frame = cap.read()
            if ret:
                self.frame(frame)

            if self._delay > 0:
                key = cv2.waitKey(int(1000 * self._delay))

            cap.release()

        cv2.destroyAllWindows()



    #
    # Properties
    #

    @property
    def show(self):
        return self._show

    @show.setter
    def show(self, value):
        self._show = value


    @property
    def delay(self):
        return self._delay

    @delay.setter
    def delay(self, value):
        self._delay = value
