import json
import os

class StreamerConfig:
    """
    Configuration data for streamer system
    """
    def __init__(self, docopt_args, config_file):
        self._camera = None         # Camera to use if camera option selected
        self._movie = None          # Movie to use if movie option selected
        self._zoom =- 1.0           # Zoom factor to use

        self._config_file = config_file
        self._docopt_args = docopt_args

        if config_file is not None:
            self._dir = os.path.dirname(config_file)

            with open(config_file, "r") as f:
                config = json.load(f)

            self._config = config

            # Get options from the config file
            if 'camera' in self._config:
                self._camera = self._config['camera']

            if 'movie' in self._config:
                self._movie = self._config['movie']

            if 'zoom' in self._config:
                self._zoom = float(self._config['zoom'])

        else:
            self._dir = os.getcwd()
            self._config = {}

        # Get options from the command line, which may overwrite
        # those from the config file
        if '--camera' in docopt_args and docopt_args['--camera'] is not None:
            self._camera = docopt_args['--camera']
            self._movie = None
        elif '--movie' in docopt_args and docopt_args['--movie'] is not None:
            self._movie = docopt_args['--movie']
            self._camera = None

        # Default to camera 1 if none provided
        if self._camera is None and self._movie is None:
            self._camera = 1

    @property
    def camera(self):
        return self._camera

    @property
    def movie(self):
        return self._movie

    @property
    def dir(self):
        if self._dir == '':
            return ''
        else:
            return self._dir + '/'

    @property
    def config(self):
        return self._config

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, value):
        self._zoom = float(value)