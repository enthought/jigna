from IPython.display import HTML

HTML_TEMPLATE = """
<div id="{div_id}">
    {html}
</div>
<script>
    $.getScript("http://{server}/jigna/js/angular.min.js", function() {{
        $.getScript("http://{server}/jigna/js/jigna.js", function() {{
            var elem = $("#{div_id}");

            elem.ready(function(){{
                angular.bootstrap(elem, ['jigna']);
            }})
        }})
    }})
</script>
"""

class JignaNotebook(object):
    def __init__(self, port=9999):
        self.server_thread = None
        self.port = port
        self._code_count = 0
        self.start_server()

    def start_server(self):
        from jigna.api import View
        view = View(body_html='')
        self.view = view
        from threading import Thread
        t = Thread(target=lambda: view.serve(port=self.port))
        t.daemon = True
        t.start()
        self.server_thread = t

    def show(self, html, **context):
        if len(context) > 0:
            self.view.update_context(**context)
        
        return HTML(self._get_html(html))

    #### Private protocol #####################################################

    def _get_html(self, html):
        server = "localhost:%d"%self.port
        div_id = 'injected%d'%self._code_count
        self._code_count += 1

        src = HTML_TEMPLATE.format(
            div_id = div_id,
            html = html,
            server = server
        )
        return src

def main():
    import _jigna_notebook_app
    _jigna_notebook_app.main()

if __name__ == '__main__':
    main()
