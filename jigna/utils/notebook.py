"""
Utility methods for the IPython notebook
"""

from jigna.api import WebApp
import threading
import time
from textwrap import dedent

app = None
call_count = 0

def display_jigna(context, template):
    """
    A `display_html` style method to show rich jigna display for the objects
    within the context.
    """
    global app, call_count

    call_count += 1

    PORT = 8005

    if not app:
        app = WebApp(context=context, template=template, port=PORT)
        t = threading.Thread(target=app.start)
        t.start()
        time.sleep(0.5)

    else:
        # Update the context being served on the web app
        app.update_context(context=context)

    from IPython.display import display_html, Javascript

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

def display_jigna2(context, template):
    """
    A `display_html` style method to show rich jigna display for the objects
    within the context.
    """
    global app, call_count

    call_count += 1

    PORT = 8005

    if not app:
        app = WebApp(context=context, template=template, port=PORT)
        t = threading.Thread(target=app.start)
        t.start()
        time.sleep(0.5)

    else:
        # Update the context being served on the web app
        app.update_context(context=context)

    from IPython.display import display_html

    server = "localhost:%d"%PORT
    div_id = 'injected%d'%call_count
    call_count += 1
    html = dedent("""
        <div id="{div_id}">
            {body_html}
        </div>
        <script>
        try {{
            jigna
            setTimeout(function() {{
                jigna.angular.compile($("#{div_id}")[0]);
            }}, 50);
        }}
        catch(err)
        {{
            window.jigna_server = "{server}";
            $.getScript("http://{server}/jigna/jigna.js", function() {{
                jigna.initialize({{async: true}});
                angular.bootstrap(document, ['jigna']);
                console.log("Started jigna.");
                setTimeout(function() {{
                    jigna.angular.compile($("#{div_id}")[0]);
                }}, 50);
            }})
        }}
        </script>
          """.format(div_id=div_id, body_html=template.body_html, server=server))
    return display_html(html, raw=True)
