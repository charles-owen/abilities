from .streamer import Streamer

class StreamerCommandLine(Streamer):

    def __init__(self,  docopt_args):
        super().__init__()

        self._docopt_args = docopt_args

        if '--camera' in docopt_args:
            self.set_camera(docopt_args['--camera'])





