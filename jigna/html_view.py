# Standard library imports
from mako.template import Template
from textwrap import dedent

# Enthought library imports
from traits.api import HasTraits, Instance, Str, Property, Int
from jigna.layout import View, Group, Item


class HTMLView(HasTraits):

    ## Traits declaration ####################################################

    model = Instance(HasTraits)

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
        return View(Group(items))

    def _get_template(self):
        if not len(self._template):
            return self.layout.render(self.model)
        else:
            return self._template

    def _set_template(self, template):
        self._template = template

    ## HTML/JS generation ####################################################

    def generate_js(self):
        template_str = dedent("""
            <%!
                from jigna.editor_factories import get_editor
                from jigna.session import PYNAME as pyobj
            %>
            <%
                obj_class = obj.__class__.__name__
            %>
            function ${obj_class}_Ctrl($scope) {
                $scope.init = function(obj_id) {
                    $scope.obj_id = obj_id;
                    % for tname in obj.editable_traits():
                        $scope.${tname} = ${pyobj}.trait_get($scope.obj_id, '${tname}');
                    % endfor
                }

                % for tname in obj.editable_traits():
                        ${get_editor(obj, tname).js()}
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
        self.js = template.render(obj=self.model)

    def generate_html(self):
        template_str = dedent("""
            <%!
                from jigna.editor_factories import get_editor
            %>
            <%
                obj_class = obj.__class__.__name__
                obj_id = id(obj)
            %>

            <div ng-controller="${obj_class}_Ctrl"
                id="id_${obj_id}"
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
