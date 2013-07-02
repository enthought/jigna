# Standard library imports
from mako.template import Template
from textwrap import dedent

# Enthought library imports
from pyface.qt import QtGui
from traits.api import HasTraits, List, Instance, Str, Property

# Local imports
from jigna.core.html_widget import HTMLWidget
from jigna.html_view import HTMLView
from jigna.util.wsgi import JinjaRenderer
from jigna.util.misc import serialize
from jigna.api import PYNAME


def show_simple_view(view):
    session = Session(views=[view])
    session.start()
    return session


class Session(HasTraits):

    views = List(Instance(HTMLView))

    resource_host = Str('resources.jigna')

    resource_url = Property(Str, depends_on='resource_host')

    html = Str

    js = Str

    css = Str

    def _get_resource_url(self):
        return 'http://{0}/'.format(self.resource_host)

    def _create_widget(self):
        hosts = {self.resource_host: JinjaRenderer(
            package='jigna',
                    template_root='resources'
        )}
        self.widget = HTMLWidget(callbacks=[('trait_set', self.trait_set),
                                            ('trait_get', self.trait_get), ],
                                 python_namespace=PYNAME,
                                 hosts=hosts,
                                 open_externally=True,
                                 debug=True
                                 )
        self.widget.create()

    def trait_set(self, model_id, tname, value):
        for view in self.views:
            if view.model_id == model_id:
                extended_name = tname.split('.')
                obj = view.model
                for attr in extended_name[:-1]:
                    obj = getattr(obj, attr)
                setattr(obj, extended_name[-1], value)

    def trait_get(self, model_id, tname):
        for view in self.views:
            if view.model_id == model_id:
                return getattr(view.model, tname)

    def _bind_trait_change_events(self, view):
        def handler(model, tname, oldValue, newValue):
            template = Template("""
                                scope = $('#id_${obj_id}').scope();
                                scope.scoped(function() {
                                    scope.${tname} = JSON.parse('${value}');
                                })
                                """)
            traitchange_js = template.render(obj_id=id(model), tname=tname,
                                             value=serialize(newValue))
            self.widget.execute_js(traitchange_js)

        view.model.on_trait_change(handler)

    def bind_all_trait_change_events(self):
        for view in self.views:
            self._bind_trait_change_events(view)

    def start(self):
        app = QtGui.QApplication.instance() or QtGui.QApplication([])
        self.create()
        app.exec_()

    def create(self):
        self._create_widget()
        self.create_py_html_bridge()
        self.widget.control.show()

    def destroy(self):
        self.html = ""
        self.js = ""
        self.widget.control.deleteLater()
        self.widget = None

    def generate_js(self):
        model_classes = []
        self.js = ""
        for view in self.views:
            if not view.model.__class__ in model_classes:
                model_classes.append(view.model.__class__)
                view.generate_js()
                self.js += view.js + "\n"

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
                        <%
                            view.generate_html()
                        %>
                        ${view.html}
                    % endfor
                </body>
            </html>
            """)
        template = Template(template_str)
        self.html = template.render(views=self.views,
                                    jquery=self.resource_url+'jquery.min.js',
                                    angular=self.resource_url+'angular.min.js',
                                    jignajs=self.js, jignacss=self.css)

    def create_py_html_bridge(self):
        self.generate_js()
        self.generate_html()
        self.bind_all_trait_change_events()
        self.widget.load_html(self.html)

    def add_view(self, view):
        self.views.append(view)
        if self.widget:
            self.create()
        else:
            view.generate_js_html()
            self.widget.execute_js("""
                $('body').append(${html});
                """.render(html=view.html))
            self.widget.execute_js(view.js)
            self._bind_trait_change_events(view)
