# Standard library imports
from mako.template import Template
from textwrap import dedent
import json
from bs4 import BeautifulSoup

# Enthought library imports
from traits.api import HasTraits, Instance, Str, Property, Int, Dict, Bool, List
from traitsui.api import View, Item, Group

# Local imports
from jigna.layout import JItem, get_items, render_layout
from jigna.session import Session
from jigna.util.misc import serialize
import jigna.registry as registry

class HTMLView(HasTraits):

    ## Traits declaration ####################################################

    model = Instance(HasTraits)

    session = Instance(Session)

    model_name = Property(Str, depends_on='model')
    _model_name = Str

    # TraitsUI View object to dictate layout
    layout = Instance(View)

    # HTML string for the view
    html = Property(Str, depends_on='layout')
    _html = Str

    # JS code for the view
    js = Str

    # CSS styles for the view
    css = Str

    def jignify(self, raw_html):
        """ Adds some magic attributes to a raw html file to make all the bindings
        work.
        """
        soup = BeautifulSoup(raw_html)
        for tag in soup.find_all(attrs={'data-model-name': self.model_name}):
            model_class = self.model.__class__.__name__
            tag['ng-controller'] = "window.%s_Ctrl" % model_class
            tag['class'] = "class_%s" % model_class
            tag['ng-init'] = "init('%s')" % self.model_name
        return soup.prettify()

    ## Private traits #######################################################

    _registered = Bool(False)

    editors = Property(List, depends_on='layout', cached=True)

    visible_traits = Property(List, depends_on='layout', cached=True)

    ## Trait property getters/setters and default methods ###################

    def _get_model_name(self):
        if not len(self._model_name):
            return str(id(self.model))
        else:
            return self._model_name

    def _set_model_name(self, model_name):
        self._model_name = model_name

    def _layout_default(self):
        items = []
        for tname in self.model.editable_traits():
            items.append(Item(name=tname))
        return View(Group(*items))

    def _get_editors(self):
        editors = []
        for item in get_items(self.layout):
            jitem = JItem(item, self.model)
            editors.append(jitem.editor)
        return editors

    def _get_visible_traits(self):
        visible_traits = []
        for item in get_items(self.layout):
            value = getattr(self.model, item.name)
            try:
                json.dumps(value)
            except TypeError:
                # catch unserializable traits here
                pass
            else:
                visible_traits.append(item.name)
        return visible_traits

    def _js_default(self):
        if not self._registered:
            registry.add_model(self.model_name, self.model)
            registry.add_view(self.model_name, self)
            self._registered = True
        if self.model.__class__ in registry.registry['model_classes']:
            return ""
        else:
            registry.add_model_class(self.model.__class__)
            template_str = dedent("""
                <%!
                    from jigna.api import PYNAME as pyobj
                %>
                <%
                        obj_class = obj.__class__.__name__
                %>
                window.${obj_class}_Ctrl = function ${obj_class}_Ctrl($scope) {
                    $scope.init = function ${obj_class}_Ctrl_init(obj_name) {
                        $scope.obj_name = obj_name;
                        % for tname in visible_traits:
                            $scope.${tname} = null;
                            $scope.$watch('${tname}', function watch_${tname}(newValue, oldValue) {
                                ${pyobj}.set_trait($scope.obj_name, '${tname}', JSON.stringify(newValue));
                            }, true);
                        % endfor
                    }

                    // editor specific JS
                    % for editor in editors:
                        ${editor.js()}
                    % endfor

                    // utility functions
                    $scope.scoped = function scoped() {
                        var func, largs;
                        func = arguments[0], largs = 2 <= arguments.length ? \
                                __slice.call(arguments, 1) : [];
                        if ($scope.$$phase) {
                        return func.apply(this, largs);
                        } else {
                        return $scope.$apply(function apply_in_scope() {
                            return func.apply(this, largs);
                        });
                        }
                    };
                }
                """)
            template = Template(template_str)
            return template.render(obj=self.model, editors=self.editors,
                                   visible_traits=self.visible_traits,
                                   dumps=json.dumps)

    def _get_html(self):
        if not len(self._html):
            template_str = dedent("""
                            <div data-model-name="${obj_name}">
                                ${rendered_layout}
                            </div>
                            """)
            raw_html = Template(template_str).render(obj_name=self.model_name,
                              rendered_layout=render_layout(self.layout, self.model))
        else:
            raw_html = self._html
        return self.jignify(raw_html)

    def _set_html(self, html):
        self._html = html
