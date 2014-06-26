# Standard library imports
import threading
import mimetypes
import sys
import os
import logging
from os.path import dirname, exists, join, sep

# Enthought library imports
from traits.api import HasTraits, Str, Dict, Directory, on_trait_change

mimeLock = threading.Lock()
mimeInitialized = False

logger = logging.getLogger(__name__)

def guess_type(content):
    """ Thread-safe wrapper around the @#%^$$# non-thread safe mimetypes module. NEVER
        call mimetypes directly. """
    global mimeLock
    global mimeInitialized

    if not mimeInitialized:
        with mimeLock:
            if not mimeInitialized:
                mimetypes.init()
                mimeInitialized = True
    return mimetypes.guess_type(content)


class FileLoader(HasTraits):

    #: Root directory where it looks
    root = Directory

    #### WSGI protocol ########################################################

    def __call__(self, env, start_response):

        path = env['PATH_INFO'].strip('/')
        path = '/'.join(path.split('/')[1:]) # remove the top-level path as that's url pattern
        path = path.replace('/', sep)        # handle Windows paths
        path = join(self.root, path)

        if not exists(path):
            start_response('404 File not found', [])
            return ""

        else:
            start_response('200 OK', [('Content-Type', guess_type(path))])
            with open(path, 'rb') as f:
                response = f.read()
            return response
