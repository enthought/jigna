# Standard library imports
from mako.template import Template
from textwrap import dedent

# Enthought library imports
from pyface.qt import QtGui
from traits.api import HasTraits, List, Instance, Str, Property, Any

# Local imports
from jigna.core.html_widget import HTMLWidget
from jigna.util.wsgi import JinjaRenderer
from jigna.api import PYNAME
import jigna.registry as registry


def show_simple_view(view):
    session = Session(views=[view])
    session.start()
    return session


class Session(HasTraits):

    views = List(Any)

    resource_host = Str('resources.jigna')

    resource_url = Property(Str, depends_on='resource_host')

    html = Str

    js = Str

    css = Str

    def _get_resource_url(self):
        return 'http://{0}/'.format(self.resource_host)

    ## Private interface ####################################################

    def _create_widget(self):
        hosts = {self.resource_host: JinjaRenderer(
                            package='jigna',
                            template_root='resources'
                )}
        self.widget = HTMLWidget(callbacks=[('set_trait', self.set_trait),
                                            ('get_trait', self.get_trait)],
                                 python_namespace=PYNAME,
                                 hosts=hosts,
                                 open_externally=True,
                                 debug=True
                                 )
        self.widget.create()

    def _create_py_html_bridge(self):
        for view in self.views:
            view.setup_session(self)
        self.generate_js_html()
        self.widget.load_html(self.html)

    ## Callbacks exposed to the QWebView ####################################

    def set_trait(self, model_id, tname, value):
        model = registry.registry['objects'].get(model_id)
        if model:
            setattr(model, tname, value)

    def get_trait(self, model_id, tname):
        model = registry.registry['objects'].get(model_id)
        if model:
            return getattr(model, tname)

    ## Public API ##########################################################

    def start(self):
        app = QtGui.QApplication.instance() or QtGui.QApplication([])
        self.create()
        app.exec_()

    def create(self):
        self._create_widget()
        self._create_py_html_bridge()
        self.widget.control.show()

    def destroy(self):
        self.html = ""
        self.js = ""
        self.widget.control.deleteLater()
        self.widget = None
        registry.clean()

    def add_view(self, view):
        self.views.append(view)
        if self.widget:
            self.create()
        else:
            self.setup(view)
            set_html_cmd = "$('body').append(${html});".render(html=view.html)
            self.widget.execute_js(set_html_cmd)
            self.widget.execute_js(view.js)

    def generate_html(self):
        template_str = dedent("""
            <html ng-app>
                <head>
                    <script type="text/javascript" src="${jquery}"></script>
                    <script type="text/javascript" src="${angular}"></script>
                    <script type="text/javascript">
                        ${jignajs}
                    </script>

                    <style>
                        ${jignacss}
                    </style>
                </head>
                <body>
                    % for view in views:
                        ${view.html}
                    % endfor
                </body>
            </html>
            """)
        template = Template(template_str)
        self.html = template.render(views=self.views,
                                    jquery=self.resource_url+'js/jquery.min.js',
                                    angular=self.resource_url+'js/angular.min.js',
                                    jignajs=self.js, jignacss=self.css)

    def generate_js(self):
        self.js = ""
        for view in self.views:
            self.js += view.js + "\n"

    def generate_js_html(self):
        self.generate_js()
        self.generate_html()
