#
# Enthought product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#


# Standard library.
import json
from mako.template import Template
from traits.api import HasTraits, Str

# Jigna libary.
from jigna.core.html_widget import HTMLWidget
from jigna.core.wsgi import JinjaRenderer


PYNAME   = "jigna"
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
};
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

JS_TO_PYTHON_BINDING_TEMPLATE = """
$scope.${obj_name}.${traitname} = ${value};
$scope.$watch('${obj_name}.${traitname}', function(newValue, oldValue) {
    ${PYNAME}.set_trait('${traitname}', JSON.stringify(newValue))
})
"""

PYTHON_TO_JS_BINDING_TEMPLATE = """
var set_${traitname}_in_scope = function(index) {
  $scope = $(this).scope();
  scoped(
    $scope,
    function set_trait_func() {
      $scope.${obj_name}.${traitname} = JSON.parse('${new_value}');
    }
  );
};

var set_${obj_name}_trait_later = function() {
  $("[data-model-name='${obj_name}']").each(set_${traitname}_in_scope);
};

setTimeout(set_${obj_name}_trait_later, 0);
"""

class JignaView(HasTraits):
    """ A factory for HTML/AngularJS based user interfaces. """

    #### 'JignaView' protocol #################################################

    #: The HTML for the *body* of the view's document.
    html = Str

    def show(self, model):
        """ Create and show a view of the given model. """

        self._widget = self._create_widget(model)
        self._bind(self._widget, model)
        self._load(self._widget)
        self._widget.control.show()

        return

    #### Private protocol #####################################################

    def _bind(self, widget, model):
        """ Bind the model in the widget.

        This sets up the two-way binding from Python->JS and back.

        """

        self._bind_python_to_js(widget, model)
        self._bind_js_to_python(widget, model)

        return

    def _bind_js_to_python(self, widget, model):
        """ Bind the model from JS-> Python. """

        traitwatcher_js = ""
        for traitname in model.editable_traits():
            traitwatcher_js += self._get_controller_js(model, traitname)

        controller_js_template = Template(CONTROLLER_JS_TEMPLATE)

        self._controller_js = controller_js_template.render(
            obj             = model,
            traitwatcher_js = traitwatcher_js,
            OBJ_NAME        = OBJ_NAME
        )

        return

    def _bind_python_to_js(self, widget, model):
        """ Bind the model from Python->JS. """

        for traitname in model.editable_traits():
            model.on_trait_change(self._on_model_trait_changed, traitname)

        return

    def _create_traitchange_js(self, model, traitname, new_value):
        """ Get the JS to update the view when the model has changed. """

        js = Template(PYTHON_TO_JS_BINDING_TEMPLATE).render(
            obj_name  = OBJ_NAME,
            traitname = traitname,
            new_value = json.dumps(new_value)
        )

        return js

    def _create_widget(self, model):
        """ Create the HTML widget that we use to render the view. """

        hosts = {
            'resources.jigna': JinjaRenderer(
                package       = 'jigna',
                template_root = 'resources'
            )
        }

        def set_trait(traitname, value_json):
            """ Set a trait on the model. """

            value = json.loads(value_json)
            setattr(model, traitname, value)

            return

        widget = HTMLWidget(
            callbacks        = [('set_trait', set_trait)],
            python_namespace = PYNAME,
            hosts            = hosts,
            open_externally  = True,
            debug            = True
        )
        widget.create()

        return widget

    def _get_controller_js(self, model, traitname):
        js = Template(JS_TO_PYTHON_BINDING_TEMPLATE).render(
            traitname = traitname,
            value     = repr(getattr(model, traitname)),
            PYNAME    = PYNAME,
            obj_name  = OBJ_NAME
        )

        return js

    def _load(self, widget):
        document_html_template = Template(DOCUMENT_HTML_TEMPLATE)
        document_html = document_html_template.render(
            jquery        = 'http://resources.jigna/js/jquery.min.js',
            angular       = 'http://resources.jigna/js/angular.min.js',
            controller_js = self._controller_js,
            body_html     = self.html
        )
        widget.load_html(document_html)

        return

    #### Trait change handlers ################################################

    def _on_model_trait_changed(self, model, traitname, new_value):
        """ Called when any trait on the model has been changed. """

        js = self._create_traitchange_js(model, traitname, new_value)
        self._widget.execute_js(js)

        return

#### EOF ######################################################################
