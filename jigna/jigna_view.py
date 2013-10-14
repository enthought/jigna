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


PYNAME   = "python"
MODEL_NAME = "model"

#### HTML templates ###########################################################

DOCUMENT_HTML_TEMPLATE = """
<html ng-app>
  <head>
    <script type="text/javascript" src="${jquery}"></script>
    <script type="text/javascript" src="${angular}"></script>
    <script type="text/javascript" src="${jigna}"></script>
    <script type='text/javascript'>
        $(document).ready(function(){
            ${initial_js}
            ${binding_js}
        })
    </script>
  </head>

  <body>
    ${body_html}
  </body>
</html>
"""

#### JS templates #############################################################

ADD_MODEL_TO_JS_TEMPLATE = """
jigna.add_model('${MODEL_NAME}', ${traits});
"""

SET_TRAIT_IN_JS_TEMPLATE = """
jigna.scope.${MODEL_NAME}.set_trait_in_js('${traitname}', ${value});
"""

SETUP_JS_WATCHER_TEMPLATE = """
jigna.scope.${MODEL_NAME}.setup_js_watcher('${traitname}');
"""

class JignaView(HasTraits):
    """ A factory for HTML/AngularJS based user interfaces. """

    #### 'JignaView' protocol #################################################

    #: The HTML for the *body* of the view's document.
    html = Str

    def show(self, model, traits=None):
        """ Create and show a view of the given model. """

        self._widget = self._create_widget(model)
        self._bind(self._widget, model, traits)
        self._load(self._widget)
        self._widget.control.show()

        return

    #### Private protocol #####################################################

    def _bind(self, widget, model, traits):
        """ Bind the model in the widget.

        This sets up the two-way binding from Python->JS and back.

        """
        if traits is None:
            traits = model.editable_traits()

        self._set_initial_js(widget, model, traits)
        self._bind_js_to_python(widget, model, traits)
        self._bind_python_to_js(widget, model, traits)

        return

    def _bind_js_to_python(self, widget, model, traits):
        """ Bind the model from JS-> Python. """

        js = ""

        for traitname in traits:
            js += Template(SETUP_JS_WATCHER_TEMPLATE).render(
                MODEL_NAME = MODEL_NAME,
                traitname  = traitname
            )

        self._binding_js = js

        return

    def _bind_python_to_js(self, widget, model, traits):
        """ Bind the model from Python->JS. """

        for traitname in traits:
            model.on_trait_change(self._on_model_trait_changed, traitname)

        return

    def _create_widget(self, model):
        """ Create the HTML widget that we use to render the view. """

        hosts = {
            'resources.jigna': JinjaRenderer(
                package       = 'jigna',
                template_root = 'resources'
            )
        }

        def set_trait(model_name, traitname, value_json):
            """ Set a trait on the model. """

            value = json.loads(value_json)
            setattr(model, traitname, value)

            return

        def get_trait(model_name, traitname):
            return json.dumps(getattr(model, traitname))


        widget = HTMLWidget(
            callbacks        = [('set_trait', set_trait),
                                ('get_trait', get_trait)],
            python_namespace = PYNAME,
            hosts            = hosts,
            open_externally  = True,
            debug            = True
        )
        widget.create()

        return widget

    def _get_add_model_js(self, model, traits):
        ADD_MODEL_TO_JS_TEMPLATE = """
            jigna.add_model('${MODEL_NAME}', ${traits});
        """

        js = Template(ADD_MODEL_TO_JS_TEMPLATE).render(
            MODEL_NAME = MODEL_NAME,
            traits     = traits
        )

        return js

    def _load(self, widget):
        document_html_template = Template(DOCUMENT_HTML_TEMPLATE)
        document_html = document_html_template.render(
            jquery        = 'http://resources.jigna/js/jquery.min.js',
            angular       = 'http://resources.jigna/js/angular.min.js',
            jigna         = 'http://resources.jigna/js/jigna.js',
            binding_js    = getattr(self, '_binding_js', ""),
            initial_js    = getattr(self, '_initial_js', ""),
            body_html     = self.html
        )
        widget.load_html(document_html)

        return

    def _set_initial_js(self, widget, model, traits):

        # First add the model to jigna
        js = self._get_add_model_js(model, traits)

        # Now set the traits in JS to give them initial value
        for traitname in traits:
            js += Template(SET_TRAIT_IN_JS_TEMPLATE).render(
                MODEL_NAME = MODEL_NAME,
                traitname  = traitname,
                value      = repr(getattr(model, traitname))
            )

        self._initial_js = js

        return


    #### Trait change handlers ################################################

    def _on_model_trait_changed(self, model, traitname, new_value):
        """ Called when any trait on the model has been changed. """

        js = Template(SET_TRAIT_IN_JS_TEMPLATE).render(
            MODEL_NAME  = MODEL_NAME,
            traitname = traitname,
            value = json.dumps(new_value)
        )

        self._widget.execute_js(js)

        return

#### EOF ######################################################################
