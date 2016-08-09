#
# Enthought product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#

""" General utility methods for the web version """

import socket

def get_free_port():
    """
    Returns a free socket port. It works by creating an empty socket, binding it
    to port 0 so that the OS automatically assigns a free port to it, obtaining
    the port using `getsockname` and then immediately closing it.

    The application intending to use this port should bind to it immediately so
    that no other application binds to it before us.
    """
    sock = socket.socket()

    # bind to a random port (so that the OS automatically assigns us a free port)
    sock.bind(('', 0))

    # obtain the random port value
    port = sock.getsockname()[1]

    # close the socket so that the port gets free
    sock.close()

    return port


def start_web_app(template, context, port=8000):
    """
    Start a web app at the given port for serving the jigna view for the given
    template and context.
    """
    from tornado.ioloop import IOLoop
    from jigna.web_app import WebApp

    ioloop = IOLoop.instance()

    app = WebApp(template=template, context=context)
    app.listen(port)

    print('Starting the web app on port %s ...' % port)
    ioloop.start()
