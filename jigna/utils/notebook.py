"""
Utility methods for the IPython notebook
"""

from jigna.api import WebApp
from IPython.display import HTML

def display_jigna(context, template, size=None):
    """
    A `display_html` style method to show rich jigna display for the objects
    within the context.
    """
    PORT = _get_free_port()

    app = WebApp(context=context, template=template, port=PORT)
    application = app.create_application()
    application.listen(app.port)

    width, height = size or template.recommended_size
    html = ('<iframe src="http://localhost:%s" width=%s height=%s></iframe>'
            % (PORT, width, height))

    return HTML(html)

def _get_free_port():
    """
    Return a free socket port. It works by creating an empty socket, binding it
    to port 0 so that the OS automatically assigns a free port to it, obtaining
    the port using `getsockname` and then immediately closing it.

    The application intending to use this port should bind to it immediately so
    that no other application binds to it before us.
    """
    import socket
    sock = socket.socket()

    # bind to a random port
    sock.bind(('', 0))

    # obtain the random port value
    port = sock.getsockname()[1]

    # close the socket so that the port gets free
    sock.close()

    return port
