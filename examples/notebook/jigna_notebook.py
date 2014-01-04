from IPython.display import HTML
from textwrap import dedent


class JignaNotebook(object):
    def __init__(self, port=9999):
        self.server_thread = None
        self.port = port
        self._code_count = 0

    def start_server(self):
        from jigna.api import View
        view = View(body_html='')
        self.view = view
        from threading import Thread
        t = Thread(target=lambda: view.serve(port=self.port))
        t.daemon = True
        t.start()
        self.server_thread = t

    def add_models(self, **context):
        self.view.update_context(**context)

    def get_ipython_html(self, body_html):
        server = "localhost:%d"%self.port
        div_id = 'injected%d'%self._code_count
        self._code_count += 1
        src = dedent("""
            <div id="{div_id}">
                {body_html}
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
              """.format(div_id=div_id, body_html=body_html, server=server))
        return src

    def show(self, body_html, **context):
        if len(context) > 0:
            self.add_models(**context)
        return HTML(self.get_ipython_html(body_html))



def main():
    import _jigna_notebook_app
    _jigna_notebook_app.main()

if __name__ == '__main__':
    main()
else:
    jigna_nb = JignaNotebook()
    jigna_nb.start_server()
    show = jigna_nb.show
