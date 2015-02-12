"""
Utility methods for the IPython notebook
"""

from jigna.api import WebApp
from jigna.utils.web import get_free_port
from IPython.display import HTML

def display_jigna(context, template, size=None):
    """
    A `display_html` style method to show rich jigna display for the objects
    within the context.
    """
    PORT = get_free_port()

    app = WebApp(context=context, template=template, port=PORT)
    application = app.create_application()
    application.listen(app.port)

    width, height = size or template.recommended_size
    html = ('<iframe src="http://localhost:%s" width=%s height=%s></iframe>'
            % (PORT, width, height))

    return HTML(html)
