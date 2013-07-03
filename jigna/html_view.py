# Standard library imports
from mako.template import Template
from textwrap import dedent

# Enthought library imports
from traits.api import HasTraits, Instance, Str, Property, Int
from jigna.layout import View, Group, Item
from jigna.session import Session
from jigna.util.misc import serialize
import jigna.registry as registry

class HTMLView(HasTraits):

    ## Traits declaration ####################################################

    model = Instance(HasTraits)

    session = Instance(Session)

    html = Str

    js = Str

    css = Str

    model_id = Property(Int, depends_on='model')

    # TraitsUI View object to dictate layout
    layout = Instance(View)

    # HTML template.
    template = Property(Str, depends_on='layout')
    _template = Str

    # Location relative to which the resource urls (css/js/images) are given in
    # the html_template
    base_url = Str

    def _get_model_id(self):
        return id(self.model)

    def _layout_default(self):
        items = []
        for tname in self.model.editable_traits():
            items.append(Item(name=tname))
        return View(Group(*items))

    def _get_template(self):
        if not len(self._template):
            return self.layout.render(self.model)
        else:
            return self._template

    def _set_template(self, template):
        self._template = template

    ## HTML/JS generation ####################################################

    def generate_js(self):
        if self.model.__class__ in registry.registry['classes']:
            self.js = ""
        else:
            template_str = dedent("""
                <%!
                    from jigna.editor_factories import get_editor
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
                            ${get_editor(obj, tname, obj_view=obj_view).js()}
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
            self.js = template.render(obj=self.model, obj_view=self)

    def generate_html(self):
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
        self.html = template.render(obj=self.model,
                                    template=self.template)

    def generate_js_html(self):
        self.generate_js()
        self.generate_html()

    def bind_trait_change_events(self):
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
            self.session.widget.execute_js(traitchange_js)

        self.model.on_trait_change(handler)

    def setup_session(self, session=None):
        """ Setup a session - initialize the session, register
        the model object and class, bind PY-JS events and generate the view's
        html/js.
        """
        if not self.session:
            self.session = session
        self.bind_trait_change_events()
        self.generate_js_html()
        registry.add_object(self.model)
        registry.add_class(self.model.__class__)
