from calibration import Calibration
from fullscreenshow import FullscreenShow
from generalcamera import GeneralCamera
import numpy as np
import cv2
import yaml
import json
import os
import math


class ProjectorCalibration(Calibration):

    def __init__(self):
        super().__init__()

        self._omits = []
        self._screen_id = 2
        self._camera_id = None
        self._camera_calibration = Calibration()

        self._zoom = 1.0
        self._invert = False
        self._surfaces = []
        self._projected_corners = {}
        self._write = None

    def args(self, args):
        config_file = args['<config-file>']
        dirname = os.path.dirname(config_file)

        with open(config_file, "r") as f:
            config = json.load(f)

        self._screen_id = int(config['screen'])
        self._camera_id = config['camera']
        if 'invert' in config:
            self._invert = config['invert']

        camera_calibration_file = config['camera-calibration']
        self._camera_calibration.read(dirname + '/' + camera_calibration_file)
        self._write = dirname + '/' + config['write']

        self._surfaces = config['surfaces']

    def calibrate(self):
        self._project_markers()
        if not self._camera_capture():
            return False

        # cv2.waitKey()
        cv2.destroyAllWindows()
        return True

    def _camera_capture(self):
        camera = GeneralCamera(camera=self._camera_id)
        if not camera.open():
            print("Unable to open camera")
            return False

        while True:
            ret, frame = camera.read()

            # Detect the markers
            corners, ids = self._detect_markers(frame)

            # Draw a coordinate axis and the surfaces
            frame = self._draw_on_frame(frame)

            # Zoom and invert support
            if self._zoom != 1.0:
                frame = cv2.resize(frame, (0, 0), fx=self._zoom, fy=self._zoom)

            if self._invert:
                frame = cv2.rotate(frame, cv2.ROTATE_180)

            cv2.imshow('frame', frame)
            key = cv2.waitKey(1) & 0xff

            if key == ord('-'):
                self._zoom /= 2

            if key == ord('+'):
                self._zoom *= 2

            if key == ord(' '):
                # Calibrate!
                if self._compute_calibration(corners, ids):
                    print(f'Writing projector calibration to to {self._write}')
                    self.write(self._write)

            if key == ord('q') or key == 27:
                break


    def _compute_calibration(self, detected_corners, detected_ids):
        world_points = []
        image_points = []

        for s in range(0, len(self._surfaces)):
            surface = self._surfaces[s]
            surface_corners = detected_corners[s]
            surface_ids = detected_ids[s]

            # Points on the surface
            p0 = self.tuple_to_column_matrix(surface[0])
            p1 = self.tuple_to_column_matrix(surface[1])
            p2 = self.tuple_to_column_matrix(surface[2])

            # Compute the surface normal
            vp1 = np.subtract(p1, p0)
            vp2 = np.subtract(p2, p0)
            n = self.cross(vp1, vp2)
            l = np.linalg.norm(n)
            n = n / l

            for i in range(0, len(surface_corners)):
                corners = surface_corners[i]
                id = surface_ids[i][0]

                # Find it in the markers we generated
                if id not in self._projected_corners:
                    continue

                for j in range(0, 4):
                    detected_corner = corners[0][j]
                    projected_corner = self._projected_corners[id][j]

                    o, d = self._camera_calibration.unproject(detected_corner[0], detected_corner[1])

                    # Compute the intersection with the surface
                    dn = self.dot(d, n)
                    if dn != 0:
                        t = self.dot(p0 - o, n) / dn
                        world_point = self.ray_point(o, d, t)

                        world_points.append(world_point)
                        image_points.append(projected_corner)

        # Now we have the world points and image points, compute the calibration
        if len(self._surfaces) > 1:
            return self._compute_calibration3d(world_points, image_points)
        else:
            return self._compute_calibration2d(world_points, image_points)

    def _compute_calibration3d(self, world_points, image_points):
        '''
        Given world points and image points, compute a 3d projector calibration
        :param world_points: World points
        :param image_points: Corresponding image points
        :return: True if successful
        '''

        try:
            wp = np.array([world_points], dtype=np.float32)
            ip = np.array([image_points], dtype=np.float32)
            flags = cv2.CALIB_FIX_K4 | cv2.CALIB_FIX_K5 | cv2.CALIB_USE_INTRINSIC_GUESS

            hit, wid = self.imsize
            initial_camera_matrix = np.array([[wid/2, 0, wid/2], [0, hit/2, hit/2], [0, 0, 1]])

            ret, self.mtx, self.dist, self.rvecs, self.tvecs = (
                cv2.calibrateCamera(wp, ip, self.imsize, initial_camera_matrix, None, None, None, flags))

            if not ret:
                print(f'Calibration failed - false return value')
                return False

        except Exception as err:
            print(f'Calibration failed: {err}')
            return False

        self._valid = True
        return True

    def _compute_calibration2d(self, world_points, image_points):
        '''
        Given world points and image points, compute a 2d projector calibration
        :param world_points: World points
        :param image_points: Corresponding image points
        :return: True if successful
        '''
        # For now we'll assume this is only for points in the xy plane with Z = 0
        world_points2d = []
        for p in world_points:
            world_points2d.append([p[0], p[1]])

        wp = np.array([world_points2d], dtype=np.float32)
        ip = np.array([image_points], dtype=np.float32)
        M, mask = cv2.findHomography(wp, ip)
        self.mtx = M
        self.dist = None
        self.rvecs = None
        self.tvecs = None
        # print(M)
        #
        # # Test loop
        # for i in range(0, len(world_points)):
        #     w1 = world_points[i]
        #     w1n = np.array([[w1[0]], [w1[1]], [1]])
        #     i1 = image_points[i]
        #
        #     i2 = M @ w1n
        #     i3 = [i2[0] / i2[2], i2[1] / i2[2]]
        #
        #     pass

        self._valid = True
        return True


    @staticmethod
    def tuple_to_column_matrix(p):
        return np.array([[p[0]], [p[1]], [p[2]]], dtype=np.float32)

    @staticmethod
    def dot(p1, p2):
        return p1[0][0] * p2[0][0] + p1[1][0] * p2[1][0] + p1[2][0] * p2[2][0]

    @staticmethod
    def ray_point(o, d, t):
        return [o[0][0] + d[0][0] * t, o[1][0] + d[1][0] * t, o[2][0] + d[2][0] * t]

    @staticmethod
    def sub(p1, p2):
        # Compute p1 - p2 as 3d vector
        return p1[0] - p2[0], p1[1] - p2[1], p1[2] - p2[2]

    @staticmethod
    def normalize(p):
        l = math.sqrt(p[0] * p[0] + p[1] * p[1] + p[2] * p[2])
        return p[0] / l, p[1] / l, p[2] / l

    @staticmethod
    def div(p1, l):
        return p1[0] / l, p1[1] / l, p1[2] / l

    @staticmethod
    def cross(v1, v2):
        return np.array([[v1[1][0] * v2[2][0] - v1[2][0] * v2[1][0]],
                         [v1[2][0] * v2[0][0] - v1[0][0] * v2[2][0]],
                         [v1[0][0] * v2[1][0] - v1[1][0] * v2[0][0]]], dtype=np.float32)

    def _detect_markers(self, frame):
        """
        Detect the aruco markers in a frame

        Returns two arrays of arrays, representing the markers found that
        intersect each surface

        :param frame: Frame to detect the markers is
        :return: Detected marker corners and ids
        """
        markerCorners, markerIds, rejectedCandidates = self._detector.detectMarkers(frame)

        surfacesMarkersCorners = []
        surfacesMarkersIds = []
        c = 0
        colors = [(255, 0, 0), (0, 0, 255), (0, 255, 0)]

        # Filter to only those within one of the provided surfaces
        for surface in self._surfaces:
            projected = self._project_surface(surface)
            projected1 = np.array(projected, dtype=np.float32)

            surfaceMarkersCorners = []
            surfaceMarkersIds = []

            for i in range(0, len(markerCorners)):
                corners = markerCorners[i]
                id = markerIds[i]

                all = True
                for corner in corners[0]:
                    if cv2.pointPolygonTest(projected1, corner, False) < 0:
                        all = False

                if all:
                    surfaceMarkersCorners.append(corners)
                    surfaceMarkersIds.append(id)

            surfacesMarkersCorners.append(surfaceMarkersCorners)
            surfacesMarkersIds.append(surfaceMarkersIds)

            surfaceMarkersIds = np.array(surfaceMarkersIds, dtype=np.int32)

            cv2.aruco.drawDetectedMarkers(frame, surfaceMarkersCorners, surfaceMarkersIds, colors[c])

            c = (c + 1) % len(colors)

        return surfacesMarkersCorners, surfacesMarkersIds

    def _draw_on_frame(self, frame):
        cc = self._camera_calibration
        cv2.drawFrameAxes(frame, cc.mtx, cc.distortion, cc.last_rvec, cc.last_tvec, 0.2)

        c = 0
        colors = [(255, 0, 0), (0, 0, 255), (0, 255, 0)]

        for surface in self._surfaces:
            projected = self._project_surface(surface)

            p_last = projected[len(projected) - 1]
            for i in range(0, len(projected)):
                p = projected[i]
                cv2.line(frame, p_last, p, colors[c], 4)
                p_last = p

                c = (c + 1) % len(colors)

        return frame

    def _project_surface(self, surface):
        projected = []

        for v in surface:
            p = self._camera_calibration.project(v[0] * 0.001, v[1] * 0.001, v[2] * 0.001)
            p = (round(p[0]), round(p[1]))
            projected.append(p)

        return projected

    def _project_markers(self):
        fullscreen = FullscreenShow('projector', self._screen_id)
        fullscreen.open()

        width, height = fullscreen.size
        # print(f"{width} {height}")
        # get the size of the screen

        image, self._projected_corners = self._create_image(width, height, 50, self._omits)
        self.imsize = image.shape

        fullscreen.imshow(image)

    def _create_image(self, width, height, size, omits):
        image = np.ones((height, width), dtype=np.float32)
        corners = {}

        # Spacing between the aruco markers as fraction of size
        spacing = int(size / 12)

        # How many rows and columns will we create?
        rows = int((height - spacing) / (size + spacing))
        cols = int((width - spacing) / (size + spacing))

        # The total height and width of all the markers on the page
        markers_height = rows * size + (rows - 1) * spacing
        markers_width = cols * size + (cols - 1) * spacing

        # Borders on top/bottom and left/right of page
        border_vertical = int((height - markers_height) / 2)
        border_horizontal = int((width - markers_width) / 2)

        dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_1000)
        self._dictionary = dictionary
        marker_id = 10

        detectionParams = cv2.aruco.DetectorParameters()
        self._detector = cv2.aruco.ArucoDetector(dictionary, detectionParams)

        row = border_vertical
        while (row + size + spacing) < height:

            col = border_horizontal
            while (col + size + spacing) < width:
                if marker_id not in omits:
                    marker_image = cv2.aruco.generateImageMarker(dictionary, marker_id, size, None, 1)
                    image[row:row + size, col:col + size] = marker_image

                    corners[marker_id] = [
                        [col, row],
                        [col + size, row],
                        [col + size, row + size],
                        [col, row + size]
                    ]

                marker_id += 1
                col += size + spacing

            row += size + spacing

        return image, corners
