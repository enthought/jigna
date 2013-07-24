# Standard library imports
from mako.template import Template
from mako.lookup import TemplateLookup
from textwrap import dedent
import os
from os.path import abspath, dirname, join
import json

# Enthought library imports
from pyface.qt import QtGui
from traits.api import Bool, HasTraits, List, Instance, Str, Property, Any

# Local imports
from jigna.core.html_widget import HTMLWidget
from jigna.util.wsgi import JinjaRenderer
from jigna.util.misc import get_value
from jigna.api import PYNAME
import jigna.registry as registry


def show_simple_view(view, *args, **kwargs):
    session = Session(views=[view], *args, **kwargs)
    session.start()
    return session


class Session(HasTraits):

    views = List(Any)

    resource_host = Str('resources.jigna')

    resource_url = Property(Str, depends_on='resource_host')

    html = Property(Str, depends_on='html_template')

    js = Str

    css = Str

    html_template = Property(Str, depends_on='_base_template')
    _html_template = Str

    # Location relative to which the resource urls (css/js/images) are given in
    # the html_template
    base_url = Str

    ######################################
    # Private traits.
    _setting_trait = Bool(False)

    _base_template = Str

    def _get_resource_url(self):
        return 'http://{0}/'.format(self.resource_host)

    def _base_url_default(self):
        return os.getcwd()

    def __base_template_default(self):
        return dedent("""
            <%!
                from jigna.api import APPNAME as appname
            %>
            <html ng-app="${appname}">
                <head>
                    <script type="text/javascript" src="${jquery}"></script>
                    <script type="text/javascript" src="${angular}"></script>

                    <%block name="extra_jigna_js"></%block>

                    <%block name="angular_app">
                        <script type='text/javascript'>
                            % for view in views:
                                ${view.js}
                            % endfor

                            <%include file="directives.mako" />
                        </script>
                    </%block>

                    % for view in views:
                        <style type="text/css">
                            ${view.css}
                        </style>
                    % endfor

                    <%block name="session_css"></%block>

                </head>
                <body>
                    <%block name="session_html">
                        % for view in views:
                            ${view.html}
                        % endfor
                    </%block>

                    <%block name="session_js"></%block>
                </body>
            </html>
            """)

    def _get_html_template(self):
        if not len(self._html_template):
            return self._base_template
        else:
            return self._html_template

    def _set_html_template(self, html_template):
        self._html_template = html_template

    ## Private interface ####################################################

    def _create_widget(self):
        hosts = {self.resource_host: JinjaRenderer(
                        package='jigna',
                        template_root='resources'
                    )
                }
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
        # to have them registered in the registry
        self.widget.load_html(self.html, self.base_url)
        d = registry.registry['models']
        for model_name, model in d.iteritems():
            view = registry.registry['views'][model_name]
            for tname in view.visible_traits:
                self._bind_trait_change_events(model, tname)
                self._update_web_ui(model, tname, eval('obj.'+tname, {'obj': model}))
            for editor in view.editors:
                editor.setup_session(session=self)

    def _get_trait_change_js(self, model, tname):
        template = Template("""
            setTimeout(function set_trait_later() {
                $("[data-model-name='${obj_name}']").each(function set_trait_in_scope(index) {
                    scope = $(this).scope();
                    scope.scoped(function set_trait_func() {
                    scope.${tname} = JSON.parse('${new_value}');
                    });
                })
            }, 0)
                """)
        obj_name = registry.registry['model_names'][id(model)]
        new_value_json = self.get_trait(obj_name, tname)
        traitchange_js = template.render(obj_name=obj_name, tname=tname,
                                         new_value=new_value_json)
        return traitchange_js

    def _bind_trait_change_events(self, model, tname):
        model.on_trait_change(self._update_web_ui, tname)

    def _update_web_ui(self, model, tname, new_value):
        if not self._setting_trait:
            traitchange_js = self._get_trait_change_js(model, tname)
            try:
                self._setting_trait = True
                self.widget.execute_js(traitchange_js)
            finally:
                self._setting_trait = False

    ## Callbacks exposed to the QWebView ####################################

    def set_trait(self, model_name, tname, value):
        if self._setting_trait:
            self._setting_trait = False
            return
        model = registry.registry['models'].get(model_name)
        if model:
            value = json.loads(value)
            if value is not None:
                self._setting_trait = True
                try:
                    setattr(model, tname, value)
                finally:
                    self._setting_trait = False

    def get_trait(self, model_name, tname):
        model = registry.registry['models'].get(model_name)
        value = json.dumps(None)
        if model:
            try:
                value = get_value(model, tname)
                value = json.dumps(value)
            except AttributeError:
                # catch event traits write only errors here
                pass
        return value

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

    def _get_html(self):
        html_template = "<%inherit file='base.html' /> \n" + self.html_template
        lookup = TemplateLookup(directories=[join(dirname(__file__), 'util')])
        lookup.put_string("base.html", self._base_template)
        lookup.put_string("template.html", html_template)
        template = lookup.get_template("template.html")

        raw_html = template.render(views=self.views,
                                   jquery=self.resource_url+'js/jquery.min.js',
                                   angular=self.resource_url+'js/angular.min.js')

        html = raw_html
        for view in self.views:
            html = view.jignify(html)
        return html