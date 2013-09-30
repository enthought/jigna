import json 
from mako.template import Template
from traits.api import HasTraits, Str

from jigna.core.html_widget import HTMLWidget
from jigna.core.wsgi import JinjaRenderer

PYNAME = "jigna"
OBJ_NAME = "model"

CONTROLLER_JS_TEMPLATE = """
    <%
        obj_class = obj.__class__.__name__
    %>
    window.scoped = function($scope, func, args) {
        if ($scope.$$phase) {
            return func.apply(this, args);
        } else {
        return $scope.$apply(function apply_in_scope() {
            return func.apply(this, args);
        });
        }
    };

    window.${obj_class} = function ${obj_class}($scope) {
        $scope.${OBJ_NAME} = {};
        ${traitwatcher_js}
    }
"""

DOCUMENT_HTML_TEMPLATE = """
    <html ng-app>
        <head>
            <script type="text/javascript" src="${jquery}"></script>
            <script type="text/javascript" src="${angular}"></script>

            <script type="text/javascript">
                ${controller_js}
            </script>
        </head>

        <body>
            ${body_html}
        </body>
    </html>

"""

class JignaView(HasTraits):

    ### Public API ################################################

    html = Str

    def show(self, model):
        self._widget = self._create_widget(model)
        self._load(self._widget)
        self._widget.control.show()

    ### Private API ##############################################

    def _bind(self, model, widget):
        self._bind_python_to_js(model, widget)
        self._bind_js_to_python(model, widget)

    def _bind_js_to_python(self, model, widget):
        traitwatcher_js = ""
        for traitname in model.editable_traits():
            traitwatcher_js += self._get_controller_js(model, traitname)

        controller_js_template = Template(CONTROLLER_JS_TEMPLATE)
        self._controller_js = controller_js_template.render(obj=model, 
                                                            traitwatcher_js=traitwatcher_js, 
                                                            OBJ_NAME=OBJ_NAME)

    def _bind_python_to_js(self, model, widget):
        for traitname in model.editable_traits():
            model.on_trait_change(self._update_web_ui, traitname)

    def _create_widget(self, model):
        hosts = {"resources.jigna": JinjaRenderer(
                        package='jigna',
                        template_root='resources'
                    )
                }

        def set_trait(traitname, value_json):
            value = json.loads(value_json)
            setattr(model, traitname, value)

        widget = HTMLWidget(callbacks=[('set_trait', set_trait)],
                            python_namespace=PYNAME, 
                            hosts=hosts,
                            open_externally=True,
                            debug=True)
        widget.create()
        self._bind(model, widget)
        return widget

    def _get_controller_js(self, model, traitname):
        js = Template("""
        $scope.${obj_name}.${traitname} = ${value};
        $scope.$watch('${obj_name}.${traitname}', function(newValue, oldValue) {
                ${PYNAME}.set_trait('${traitname}', JSON.stringify(newValue))
            })
        """).render(traitname=traitname, value=repr(getattr(model, traitname)), 
                   PYNAME=PYNAME, obj_name=OBJ_NAME)
        return js

    def _load(self, widget):
        document_html_template = Template(DOCUMENT_HTML_TEMPLATE)
        document_html = document_html_template.render(jquery='http://resources.jigna/js/jquery.min.js', 
                                                      angular='http://resources.jigna/js/angular.min.js',
                                                      controller_js=self._controller_js, 
                                                      body_html=self.html)
        widget.load_html(document_html)


    ### Trait change handlers ###################################

    def _update_web_ui(self, model, traitname, new_value):
        js = self._get_traitchange_js(model, traitname, new_value)
        self._widget.execute_js(js)

    def _get_traitchange_js(self, model, traitname, new_value):
        template = Template("""
            setTimeout(function set_trait_later() {
                $("[data-model-name='${obj_name}']").each(function set_trait_in_scope(index) {
                    $scope = $(this).scope();
                    scoped($scope, function set_trait_func() {
                        $scope.${obj_name}.${traitname} = JSON.parse('${new_value}');
                    });
                })
            }, 0)
        """)
        traitchange_js = template.render(obj_name=OBJ_NAME, traitname=traitname,
                                         new_value=json.dumps(new_value))
        return traitchange_js

    
