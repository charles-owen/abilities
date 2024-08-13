import screeninfo
import numpy as np
import cv2


class FullscreenShow:
    """
    Support for creating a full-screen OpenCV imshow window.
    """
    def __init__(self, name, screen):
        self._name = name
        self._screen = screen
        self._width = 0
        self._height = 0
        self._is_open = False

        # print(screeninfo.get_monitors())

    def open(self):
        # get the size of the screen
        monitors = screeninfo.get_monitors()
        if self._screen < 1 or self._screen > len(monitors):
            print(f'Fullscreen: screen {self._screen} is not available')
            return

        screen = screeninfo.get_monitors()[self._screen - 1]
        print(monitors)
        print(screen)
        width, height = screen.width, screen.height

        self._width = width
        self._height = height

        image = np.zeros((height, width), dtype=np.float32)

        window_name = self._name
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.moveWindow(window_name, screen.x, screen.y)
        cv2.imshow(window_name, image)

        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,
                              cv2.WINDOW_FULLSCREEN)

        self._is_open = True

    def white(self):
        if self._is_open:
            image = np.ones((self._height, self._width), dtype=np.float32)
            self.imshow(image)

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def size(self):
        return self._width, self._height

    def imshow(self, image):
        if self._is_open:
            cv2.imshow(self._name, image)
            
