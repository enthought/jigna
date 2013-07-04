# Standard library imports
from mako.template import Template
from textwrap import dedent

# Enthought library imports
from traits.api import HasTraits, Instance, Str, Property, Int, Dict, Bool

# Local imports
from jigna.layout import View, Group, Item
from jigna.session import Session
from jigna.util.misc import serialize
from jigna.editor_factories import get_editor
import jigna.registry as registry

class HTMLView(HasTraits):

    ## Traits declaration ####################################################

    model = Instance(HasTraits)

    session = Instance(Session)

    model_id = Property(Int, depends_on='model')

    # TraitsUI View object to dictate layout
    layout = Instance(View)

    # Scoped HTML template (an angularjs template)
    template = Property(Str, depends_on='layout')
    _template = Str

    # HTML string for the view
    html = Str

    # JS code for the view
    js = Str

    # CSS styles for the view
    css = Str

    # Dictionary representing the editors for each model trait
    editors = Dict

    ## Private traits #######################################################

    _registered = Bool(False)

    def _register(self):
        registry.add_model(self.model)
        registry.add_model_class(self.model.__class__)
        registry.add_view(self.model, self)
        self._registered = True

    ## Trait property getters/setters and default methods ###################

    def _get_model_id(self):
        return id(self.model)

    def _layout_default(self):
        items = []
        for tname in self.model.editable_traits():
            items.append(Item(name=tname, editor=self.editors.get(tname)))
        return View(Group(*items))

    def _get_template(self):
        if not len(self._template):
            return self.layout.render(self.model)
        else:
            return self._template

    def _set_template(self, template):
        self._template = template

    def _editors_default(self):
        editors = {}
        for tname in self.model.editable_traits():
            ttype = self.model.trait(tname).trait_type
            editors[tname] = get_editor(ttype)
        return editors

    def _js_default(self):
        if not self._registered:
            registry.add_model(self.model)
            registry.add_view(self.model, self)
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
                window.${obj_class}_Ctrl = function($scope) {
                    $scope.init = function(obj_id) {
                        $scope.obj_id = obj_id;
                        % for tname in obj.editable_traits():
                            $scope.${tname} = ${pyobj}.get_trait($scope.obj_id, '${tname}');
                        % endfor
                    }

                    % for tname in obj.editable_traits():
                            ${editors[tname](obj=obj, tname=tname).js()}
                    % endfor

                    // utility functions
                    $scope.scoped = function() {
                        var func, largs;
                        func = arguments[0], largs = 2 <= arguments.length ? \
                                __slice.call(arguments, 1) : [];
                        if ($scope.$$phase) {
                        return func.apply(this, largs);
                        } else {
                        return $scope.$apply(function() {
                            return func.apply(this, largs);
                        });
                        }
                    };
                }
                """)
            template = Template(template_str)
            return template.render(obj=self.model, editors=self.editors)

    def _html_default(self):
        template_str = dedent("""
            <%!
                from jigna.editor_factories import get_editor
            %>
            <%
                obj_class = obj.__class__.__name__
                obj_id = id(obj)
            %>

            <div ng-controller="window.${obj_class}_Ctrl"
                data-id=${obj_id}
                class="class_${obj_class}"
                ng-init="init(${obj_id})">
                    ${template}
            </div>
            """)
        template = Template(template_str)
        return template.render(obj=self.model,
                               template=self.template)
