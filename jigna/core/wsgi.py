# Standard library imports
import threading
import mimetypes
import sys
import logging
from os.path import dirname, exists, join, sep
from jinja2 import Environment, FileSystemLoader, PackageLoader

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
    

class JinjaRenderer(HasTraits):
    """ A simple interface mapping URLs to templates and rendering them.
    """
    # package to find templates in
    package = Str(None)

    # path to the template directory
    template_root = Directory

    # context to be handed passed to the template render method
    context = Dict

    # following mimetypes to be rendered using jinja (rest all are served directly)
    render_mimetypes = ["text/html"]

    @on_trait_change('package, template_root')
    def path_changed(self):
        """ Lazy-load an Environment instance and set up the
        appropriate template loader.
        """
        self._env = getattr(self, '_env', None) or Environment()
        if self.package:
            self._env.loader = PackageLoader(self.package, self.template_root)
        else:
            self._env.loader = FileSystemLoader(self.template_root)

    def template_path(self, path):
        if self.package:
            __import__(self.package)
            prefix = dirname(sys.modules[self.package].__file__)
        else:
            prefix = ''
        return join(prefix, self.template_root, path)

    def __call__(self, env, start_response):
        path = env['PATH_INFO'].strip('/')
        mime_type = guess_type(path)[0] or 'text/html'
        logger.debug('Handling request for %s, mime type %s', path, mime_type)
        path = path.replace('/', sep)

        localpath = self.template_path(path)
        if not exists(localpath):
            start_response('404 File Not Found', [])
            logger.debug('404 File Not Found: %s', localpath)
            return ""

        start_response('200 OK', [('Content-Type', mime_type)])

        if not mime_type in self.render_mimetypes:
            return open(localpath, 'rb').read()

        # jinja can not handle windows backslashes:
        if sys.platform == 'win32':
            path = path.replace('\\', '/')
        tpl = self._env.get_template(path)
        return [tpl.render(self.context).encode('utf-8')]
