"""
Utility methods for the IPython notebook
"""

from jigna.api import WebApp

call_count = 0
app = None

def display_jigna(context, template):
    """
    A `display_html` style method to show rich jigna display for the objects
    within the context.
    """
    global call_count, PORT, app

    call_count += 1

    PORT = 8005

    if not app:
        app = WebApp(context=context, template=template, port=PORT)
        application = app.create_application()
        application.listen(app.port)
    else:
        app.update_context(context=context)

    from IPython.display import display_html, Javascript, HTML

    # The Javascript code to compile the template which is added dynamically to
    # the DOM
    div_id = 'jigna-injected-' + str(call_count)
    html = """
        <div id='{div_id}'>
            {html}
        </div>
    """.format(div_id=div_id, html=template.body_html)

    display_html(html, raw=True)

    js = """
        window.jigna_server = "localhost:%s";
        jigna.initialize({async: true});
        jigna.angular.compile($("#" + %r)[0])
    """ % (PORT, div_id)

    return Javascript(js, lib='http://localhost:%s/jigna/jigna.js' % PORT)
