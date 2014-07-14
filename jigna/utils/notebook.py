"""
Utility methods for the IPython notebook
"""

from jigna.api import WebApp
from IPython.display import HTML

PORT = 8005

def display_jigna(context, template):
    """
    A `display_html` style method to show rich jigna display for the objects
    within the context.
    """
    global PORT

    PORT += 1

    app = WebApp(context=context, template=template, port=PORT)
    application = app.create_application()
    application.listen(app.port)

    width, height = template.recommended_size
    html = ('<iframe src="http://localhost:%s" width=%s height=%s></iframe>'
            % (PORT, width, height))

    return HTML(html)
