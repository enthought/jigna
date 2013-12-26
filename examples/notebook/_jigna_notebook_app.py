"""Overridden IPython notebook server to support jigna.
"""
from IPython.frontend.html.notebook.notebookapp import NotebookApp
import requests
from tornado.web import RequestHandler, URLSpec


class JignaProxy(RequestHandler):
    """A proxy to handle jigna GET requests.
    """
    def initialize(self, server):
        self.server = server

    def get(self):
        data = self.get_argument("data")
        r = requests.get("http://%s/_jigna"%self.server, params={"data":data})
        self.write(r.text)


class JignaNotebookApp(NotebookApp):
    """Overloaded to add the JignaProxy to the notebook server.
    """
    def init_webapp(self):
        super(JignaNotebookApp, self).init_webapp()
        spec = URLSpec(r"/_jigna", JignaProxy, dict(server="localhost:9999"))
        self.web_app.handlers[0][1].append(spec)


def main():
    app =  JignaNotebookApp()
    app.initialize()
    app.start()

if __name__ == '__main__':
    main()
