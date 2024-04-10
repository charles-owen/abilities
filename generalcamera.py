import cv2

try:
    from pypylon import pylon
    _has_pylon = True
except ImportError:
    _has_pylon = False

class GeneralCamera:
    """
    Class for camera frame acquisition that will work for
    both normal OpenCV VideoCapture devices and Pylon cameras

    Currently only supports on Pylon device (first device found)
    """
    def __init__(self, width=None, height=None, camera=None, prefer_pylon=True, gain=None,
                 exposure_time=None, frame_rate=None):
        """
        Constructor
        :param width: Specified desired width, default is none
        :param height: Specified desired height, default is none
        :param gain: Optional camera gain to apply in decibels (Pylon only)
        :param exposure_time: Optional exposure time in microseconds (Pylon only)
        :param frame_rate: Optional specified maximum frame rate, 0 for none (Pylon only)
        :param camera: Desired camera number starting at 1, prefix with P to specify a Pylon camera.
            If None, select first available camera
        :param prefer_pylon Set true to use Pylon camera if available
        """
        self._width = width
        self._height = height
        self._gain = gain
        self._prefer_pylon = prefer_pylon
        self._exposure_time = exposure_time
        self._frame_rate = frame_rate
        self._device = None
        self._source = None

        self._require_pylon = False
        self._require_opencv = False

        if camera is None:
            # If no camera supplied, we do not require Pylon and
            # assume the first camera
            self._camera = 1

        else:
            camera = str(camera).lower()
            if camera[0] == 'p':
                self._require_pylon = True
                self._camera = int(camera[1:])
            else:
                self._require_opencv = True
                self._camera = int(camera)


    def open(self):
        """
        Open the camera for display
        :return: True if successful
        """

        if self._require_opencv:
            # We are explicitly requiring an OpenCV camera
            return self._open_opencv(self._camera)

        if self._require_pylon:
            # We are explicitly requireing a Pylon camera
            return self._open_pylon(self._camera)

        if _has_pylon and self._prefer_pylon:
            if self._open_pylon(self._camera):
                return True

            # Fall back to OpenCV camera if Pylon open fails
            return self._open_opencv(self._camera)

        else:
            return self._open_opencv(self._camera)

    def close(self):
        if self._source == 'VideoCapture' and self._device is not None:
            self._device.release()
            self._device = None
            self._source = None

    def _open_opencv(self, index):
        self._source = 'VideoCapture'
        self._device = cv2.VideoCapture()
        if self._width is not None:
            self._device.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        if self._height is not None:
            self._device.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)

        if self._camera is None:
            return self._device.open(0)
        else:
            return self._device.open(self._camera)


    def _open_pylon(self, camera):
        """
        Try to open a Pylon camera
        :param camera: Camera number to open, starting at 1
        :return: True if successful
        """
        tlf = pylon.TlFactory.GetInstance()

        devices = []
        for d in tlf.EnumerateDevices():
            devices.append(d)
            # print(d.GetModelName())

        if len(devices) <= 0:
            return False

        self._source = 'Pylon'
        device = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(devices[camera-1]))
        self._device = device
        self._model_name = device.GetDeviceInfo().GetModelName()

        device.Open()

        if self._width is not None:
            self._device.Width.Value = self._width
        if self._height is not None:
            self._device.Height.Value = self._height
        if self._gain is not None:
            device.Gain.Value = self._gain
        if self._exposure_time is not None:
            device.ExposureTime.Value = self._exposure_time

        if self._frame_rate is not None:
            if self._frame_rate > 0:
                device.AcquisitionFrameRate.Value = self._frame_rate
                device.AcquisitionFrameRateEnable.Value = True
            else:
                device.AcquisitionFrameRateEnable.Value = False

        # Grabbing continuously (video) with minimal delay
        self._device.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        self._converter = pylon.ImageFormatConverter()

        # converting to opencv bgr format
        self._converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        self._converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

        return True

    def read(self):
        """
        Read a frame from the device. Frame is returned as an OpenCV frame
        :return: success, frame
        """
        if self._source == 'Pylon':
            grab_result = self._device.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            if grab_result.GrabSucceeded():
                # Access the image data
                image = self._converter.Convert(grab_result)
                return True, image.GetArray()
            return False, None
        elif self._source == 'VideoCapture':
            return self._device.read()
        else:
            return False, None

    @property
    def width(self):
        if self._source == 'Pylon':
            return self._device.Width.Value
        elif self._source == 'VideoCapture':
            return self._device.get(cv2.CAP_PROP_FRAME_WIDTH)
        else:
            return 0

    @property
    def height(self):
        if self._source == 'Pylon':
            return self._device.Height.Value
        elif self._source == 'VideoCapture':
            return self._device.get(cv2.CAP_PROP_FRAME_HEIGHT)
        else:
            return 0

    @property
    def has_pylon(self):
        return _has_pylon

    @property
    def source(self):
        return self._source

    @property
    def frame_rate(self):
        if self._source == 'Pylon':
            return self._device.ResultingFrameRate.Value
        else:
            return self._device.get(cv2.CAP_PROP_FPS)

