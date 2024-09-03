from .streamer import Streamer

class StreamerCommandLine(Streamer):

    def __init__(self,  docopt_args):
        super().__init__()

        self._docopt_args = docopt_args

        if '--camera' in docopt_args and docopt_args['--camera'] is not None:
            self.set_camera(docopt_args['--camera'])
        elif '--movie' in docopt_args and docopt_args['--movie'] is not None:
            self.set_movie(docopt_args['--movie'])





