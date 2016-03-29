# Standard library imports
import threading
import mimetypes
import logging
from os.path import exists, join, sep

# Enthought library imports
from traits.api import HasTraits, Str, Dict, Directory, on_trait_change

mimeLock = threading.Lock()
mimeInitialized = False

logger = logging.getLogger(__name__)


def guess_type(path):
    """ Thread-safe wrapper around the @#%^$$# non-thread safe mimetypes module. NEVER
    call mimetypes directly.

    """

    global mimeLock
    global mimeInitialized

    if not mimeInitialized:
        with mimeLock:
            if not mimeInitialized:
                mimetypes.init()

                # On Windows, the mime type for 'ttf' (True Type Fonts) isn't
                # recognized correctly. We, therefore, add the correct mime
                # type here.
                mimetypes.add_type('application/font-sfnt', '.ttf')

                mimeInitialized = True

    guessed = mimetypes.guess_type(path)

    return (guessed[0] or "", guessed[1] or "")


class FileLoader(HasTraits):

    #: Root directory where it looks
    root = Directory

    #: A dictionary of overrides which holds canned responses for some special
    #: paths
    overrides = Dict

    #### WSGI protocol ########################################################

    def __call__(self, env, start_response):

        # Clean up path and handle Windows paths
        path = env['PATH_INFO'].strip('/').replace('/', sep)

        # Check if it is handled by one of the overrides
        if self.overrides.get(path) is not None:
            start_response(
                '200 OK', [('Content-Type', '; '.join(guess_type(path)))]
            )
            return [self.overrides[path]]

        # Continue, if the path wasn't handled by canned responses for special
        # paths
        path = join(self.root, path)
        if not exists(path):
            start_response('404 File not found', [])
            return [""]

        else:
            start_response(
                '200 OK', [('Content-Type', '; '.join(guess_type(path)))]
            )
            with open(path, 'rb') as f:
                response = f.read()
            return [response]
