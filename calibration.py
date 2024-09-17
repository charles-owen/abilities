import yaml
import numpy as np
import cv2


class Calibration:
    """
    Class the stores and utilizes an OpenCV calibration
    """

    def __init__(self):
        # The image size
        self.imsize = None

        # The camera matrix
        self.mtx = None

        # Distortion statistics
        self.dist = None

        # Rotation vector
        self.rvecs = None

        # Translation vectors
        self.tvecs = None

        self._valid = False

    def set(self, imsize, mtx, dist=None, rvecs=None, tvecs=None):
        self.imsize = imsize
        self.mtx = mtx
        self.dist = dist
        self.rvecs = rvecs
        self.tvecs = tvecs
        self._valid = True

    def write(self, filename):
        """
        Write the calibration to a YAML format file
        :param filename: Filename to write
        :return: None
        """

        data = {'imsize': np.asarray(self.imsize).tolist(),
                'camera_matrix': np.asarray(self.mtx).tolist(),
                'dist_coeff': np.asarray(self.dist).tolist(),
                'rvecs': np.asarray(self.rvecs).tolist(),
                'tvecs': np.asarray(self.tvecs).tolist()}

        # and save it to a file
        with open(filename, "w") as f:
            yaml.dump(data, f)

    def read(self, filename):
        """
        Read a calibration from a YAML format tile
        :param filename: Filename to read
        :return: True if successful
        """
        with open(filename, "r") as f:
            data = yaml.safe_load(f)

        self.imsize = np.asarray(data['imsize'])
        self.mtx = np.asarray(data['camera_matrix'])
        self.dist = np.asarray(data['dist_coeff'])
        self.rvecs = np.asarray(data['rvecs'])
        self.tvecs = np.asarray(data['tvecs'])
        self._valid = True
        return True

    def project(self, x, y, z):
        """
        Project a 3D world point to the 2D image space
        :param x: X in world coordinates
        :param y: Y in world coordinates
        :param z: Z in world coordinates
        :return: u, v in screen coordinates
        """
        t, r = self.lastPose()

        # # Example of how to use projectPoints to do the projection
        # # without doing the actual projection math
        # w = np.array([[x], [y], [z]])
        #
        # # Convert point to camera coordinates
        # c = np.matmul(r, w) + t
        # coords = np.array([[c[0][0], c[1][0], c[2][0]]])
        #
        # projected,_ = cv2.projectPoints(coords, r, t, self.mtx, self.dist)
        # u = projected[0][0][0]
        # v = projected[0][0][1]

        # Implementation of OpenCV projection with
        # distortion as per:
        # https://docs.opencv.org/2.4/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html
        w = np.array([[x], [y], [z]])

        # Convert point to camera coordinates
        c = np.matmul(r, w) + t

        xp = c[0][0] / c[2][0]
        yp = c[1][0] / c[2][0]

        if self.dist is not None:
            # Distortion coefficients
            k1 = self.dist[0][0]
            k2 = self.dist[0][1]
            p1 = self.dist[0][2]
            p2 = self.dist[0][3]
            k3 = self.dist[0][4]

            r2 = xp * xp + yp * yp
            r4 = r2 * r2
            r6 = r4 * r2
            kfactor = (1 + k1 * r2 + k2 * r4 + k3 * r6)
            xpp = xp * kfactor + 2 * p1 * xp * yp + p2 * (r2 + 2 * xp * xp)
            ypp = yp * kfactor + p1 * (r2 + 2 * yp * yp) + 2 * p2 * xp * yp
        else:
            xpp = xp
            ypp = yp

        uv = np.matmul(self.mtx, np.array([[xpp], [ypp], [1]]))

        u = uv[0][0]
        v = uv[1][0]

        return u, v

    def project2d(self, x, y):
        """
        Project a 2D world point to the 2D image space
        Only works if the calibration matrix is a homography
        :param x: X in world coordinates
        :param y: Y in world coordinates
        :return: u, v in screen coordinates
        """
        w = np.array([[x], [y], [1]])
        p = self.mtx @ w
        u = p[0][0] / p[2][0]
        v = p[1][0] / p[2][0]

        return u, v

    def unproject2d(self, u, v):
        """
        Unproject an image pixels to a world x,y location
        :param u: Pixel u
        :param v: Pixel y
        :return:
        """
        p = np.array([[u], [v], [1]])
        mtx_inv = np.linalg.inv(self.mtx)
        w = mtx_inv @ p
        x = w[0][0] / w[2][0]
        y = w[1][0] / w[2][0]

        return x, y

    def unproject(self, u, v):
        """
        Convert a value in screen coordinates to a ray that
        describes the points that can project to that point in space.

        Any point that projects to u,v based on this camera calibration
        can be pressed as o + td for some t > 0

        Both o and d are a 3x1 numpy column matrix

        :param u: U screen coordinate (horizontal)
        :param v: V screen coordinate (vertical)
        :return: o, d where o is the ray origin and d is the ray direction in space.
        """
        # Remove the camera distortion
        coords = np.array([[u, v]])
        xy = cv2.undistortPoints(coords, self.mtx, self.dist)
        xp = xy[0][0][0]  # x-prime
        yp = xy[0][0][1]  # y-prime

        # This is a point on a plane parallel to the xy plane
        # relative to the camera at z=1
        p = np.array([[xp], [yp], [1.0]])

        # Convert the point and the camera origin
        # into locations in the world coordinate system

        t, r = self.lastPose()
        r_inv = np.linalg.inv(r)
        w = np.matmul(r_inv, (p - t))

        # Camera location in the world coordinate system
        o = np.matmul(r_inv, -t)

        # Direction through u,v on the screen in the world coordinate system
        d = w - o
        d = d / np.linalg.norm(d)

        return o, d

    def ray_intersect_xy(self, o, d, z):
        """
        Computer the intersection of a ray with an x,y plane

        Let o, d be the origin and direction of a ray in space.
        Compute the location x,y,z on the ray, where z is the
        supplied z value.
        :param o: Ray origin
        :param d: Ray direction
        :param z: Z value we are seeking
        :return: Computed intersection point
        """

        i = 2
        t = (z - o[i][0]) / d[i][0]
        return o + d * t

    def lastPose(self):
        # Get the last camera pose
        t = self.tvecs[len(self.tvecs) - 1]
        r, _ = cv2.Rodrigues(self.rvecs[len(self.rvecs) - 1])
        return t, r

    def lastPoseInv(self):
        t, r = self.lastPose()
        t = -t
        r = np.linalg.inv(r)
        return t, r

    @property
    def matrix(self):
        return self.mtx

    @property
    def distortion(self):
        return self.dist

    @property
    def last_tvec(self):
        return self.tvecs[len(self.tvecs) - 1]

    @property
    def last_rvec(self):
        return self.rvecs[len(self.rvecs) - 1]

    @property
    def valid(self):
        return self._valid
