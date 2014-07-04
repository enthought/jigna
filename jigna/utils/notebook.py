"""
Utility methods for the IPython notebook
"""

from jigna.api import WebApp
import threading
import time

app = None

def display_jigna(context, template):
    """
    A `display_html` style method to show rich jigna display for the objects
    within the context.
    """
    global app

    if not app:
        app = WebApp(context=context, template=template, port=8005)
        t = threading.Thread(target=app.start)
        t.start()
        time.sleep(0.5)

    else:
        # Update the context being served on the web app
        app.update_context(context=context)

    from IPython.display import Javascript

    # The Javascript code to compile the template which is added dynamically to
    # the DOM
    js = 'window.jigna_server = "localhost:%s"; jigna.initialize({async: true}); element.append(jigna.angular.compile(%r)); element.parent().show()' % (8005, template.body_html)

    return Javascript(js, lib='http://localhost:8005/jigna/jigna.js')
