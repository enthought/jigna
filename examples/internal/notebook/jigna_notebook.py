from IPython.display import display_html
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
            try {{
                jigna
                setTimeout(function() {{
                    $(document.body).scope().recompile($("#{div_id}"));
                }}, 50);
            }}
            catch(err)
            {{
                window.jigna_server = "{server}";
                $.getScript("http://{server}/jigna/js/angular.min.js", function() {{
                    $.getScript("http://{server}/jigna/js/jigna.js", function() {{
                        jigna.initialize(true);
                        angular.bootstrap(document, ['jigna']);
                        console.log("Started jigna.");
                        setTimeout(function() {{
                            $(document.body).scope().recompile($("#{div_id}"));
                        }}, 50);
                    }})
                }});
            }}
            </script>
              """.format(div_id=div_id, body_html=body_html, server=server))
        return src

    def show(self, body_html, **context):
        if len(context) > 0:
            self.add_models(**context)
        return display_html(self.get_ipython_html(body_html), raw=True)



def main():
    from IPython.frontend.html.notebook.notebookapp import NotebookApp
    app = NotebookApp()
    app.initialize()
    app.start()

if __name__ == '__main__':
    main()
else:
    jigna_nb = JignaNotebook()
    jigna_nb.start_server()
    show = jigna_nb.show
