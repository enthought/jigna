# Standard library imports
from mako.template import Template
from textwrap import dedent
import os
import json

# Enthought library imports
from pyface.qt import QtGui
from traits.api import HasTraits, List, Instance, Str, Property, Any

# Local imports
from jigna.core.html_widget import HTMLWidget
from jigna.util.wsgi import JinjaRenderer
from jigna.api import PYNAME
from jigna.util.misc import serialize
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

    # Location relative to which the resource urls (css/js/images) are given in
    # the html_template
    base_url = Str

    def _get_resource_url(self):
        return 'http://{0}/'.format(self.resource_host)

    def _base_url_default(self):
        return os.getcwd()

    ## Private interface ####################################################

    def _create_widget(self):
        hosts = {self.resource_host: JinjaRenderer(
                        package='jigna',
                        template_root='resources'
                    ),
                 'file.jigna': JinjaRenderer(
                        template_root=self.base_url
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
        # NOTE: Loading the widget html before binding trait change events is
        # necessary since we need atleast one access to view.html and view.js
        # to register them
        self.widget.load_html(self.html)
        d = registry.registry['models']
        for model_id, model in d.iteritems():
            self._bind_trait_change_events(model)
            view = registry.registry['views'][model_id]
            for tname in model.editable_traits():
                editor = view.editors[tname](obj=model, tname=tname)
                editor.setup_session(session=self)

    def _bind_trait_change_events(self, model):
        def handler(model, tname, oldValue, newValue):
            template = Template("""
                                $('[data-id=${obj_id}]').each(function(index) {
                                    scope = $(this).scope();
                                    scope.scoped(function() {
                                        scope.${tname} = JSON.parse('${value}');
                                    })
                                })
                                """)
            traitchange_js = template.render(obj_id=id(model), tname=tname,
                                             value=serialize(newValue))
            self.widget.execute_js(traitchange_js)

        model.on_trait_change(handler)

    ## Callbacks exposed to the QWebView ####################################

    def set_trait(self, model_id, tname, value):
        model = registry.registry['models'].get(model_id)
        if model:
            oldval = getattr(model, tname)
            try:
                value = type(oldval)(value)
            except ValueError:
                pass
            else:
                setattr(model, tname, value)

    def get_trait(self, model_id, tname):
        model = registry.registry['models'].get(model_id)
        if model:
            return getattr(model, tname)

    ## Public API ##########################################################

    def start(self):
        app = QtGui.QApplication.instance() or QtGui.QApplication([])
        self.create()
        app.exec_()
        registry.clean()

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

    def _html_default(self):
        template_str = dedent("""
            <html ng-app>
                <head>
                    <script type="text/javascript" src="${jquery}"></script>
                    <script type="text/javascript" src="${angular}"></script>
                    <script type="text/javascript">
                        ${jignajs}
                    </script>

                    <script type="text/javascript" href="http://file.jigna/test.js"></script>

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
        return template.render(views=self.views,
                               jquery=self.resource_url+'js/jquery.min.js',
                               angular=self.resource_url+'js/angular.min.js',
                               jignajs=self.js, jignacss=self.css)

    def _js_default(self):
        js = ""
        for view in self.views:
            js += view.js + "\n"
        return js
