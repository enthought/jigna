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
import sys

# 3rd party library.
from mako.template import Template

# Enthought library.
from traits.api import (
    Dict, HasTraits, Instance, Str, TraitInstance, TraitListEvent
)

# Jigna libary.
from jigna.core.html_widget import HTMLWidget
from jigna.core.wsgi import JinjaRenderer


#### HTML templates ###########################################################

DOCUMENT_HTML_TEMPLATE = """
<html ng-app>
  <head>
    <script type="text/javascript" src="${jquery}"></script>
    <script type="text/javascript" src="${angular}"></script>
    <script type="text/javascript" src="${jigna}"></script>
    <script type="text/javascript">
        $(document).ready(function(){
           jigna.proxy_manager.add_model('${model_name}', '${id}');
        });
    </script>
  </head>

  <body>
    ${body_html}
  </body>
</html>
"""

MODEL_NAME = "model"


class JignaView(HasTraits):
    """ A factory for HTML/AngularJS based user interfaces. """

    #### 'JignaView' protocol #################################################

    #: The HTML for the *body* of the view's document.
    html = Str

    def show(self, model):
        """ Create and show a view of the given model. """

        self._bind_python_to_js(model)

        self._widget = self._create_widget(model)

        self._widget.control.show()

        return

    #### Private protocol #####################################################

    #: The ID to model mapping.
    _id_to_object_map = Dict

    def _bind_python_to_js(self, model):
        """ Bind the model from Python->JS. """

        self._id_to_object_map[str(id(model))] = model

        model.on_trait_change(self._on_model_trait_changed)

        return

    def _create_widget(self, model):
        """ Create the HTML widget that we use to render the view. """

        hosts = {
            'resources.jigna': JinjaRenderer(
                package       = 'jigna',
                template_root = 'resources'
            )
        }

        widget = HTMLWidget(
            callbacks        = [
                ('get_instance_info', self._bridge_get_instance_info),
                ('get_list_info',     self._bridge_get_list_info),
                ('get_trait',         self._bridge_get_trait),
                ('set_trait',         self._bridge_set_trait),
            ],
            python_namespace = 'python_bridge',
            hosts            = hosts,
            open_externally  = True,
            debug            = True
        )
        widget.create()

        widget.load_html(self._generate_html(model))

        return widget

    def _generate_html(self, model):

        template = Template(DOCUMENT_HTML_TEMPLATE)
        html     = template.render(
            jquery     = 'http://resources.jigna/js/jquery.min.js',
            angular    = 'http://resources.jigna/js/angular.min.js',
            jigna      = 'http://resources.jigna/js/jigna.js',
            body_html  = self.html,
            model_name = MODEL_NAME,
            id         = id(model)
        )

        return html

    def _bridge_get_instance_info(self, id):
        """ Return a description of an instance. """

        obj = self._id_to_object_map.get(id)

        info = obj.editable_traits()
        self._bind_python_to_js(obj)

        return info

    def _bridge_get_list_info(self, id):
        """ Returns a description of a list. """

        obj = self._id_to_object_map.get(id)

        return len(obj)

    def _bridge_get_trait(self, obj_id, trait_name):
        """ Return the value of a trait on an object in the form:
        {exception, type, value}.
        """

        obj = self._id_to_object_map.get(obj_id)
        try:
            if isinstance(obj, HasTraits):
                value = getattr(obj, trait_name)

            else:
                value = obj[int(trait_name)]

            exception = None,
            type, value = self._get_type_and_value(value)

        except Exception, e:
            exception = repr(sys.exc_type),
            type      = 'exception',
            value     = repr(sys.exc_value)

        return dict(exception=None, type=type, value=value)

    def _bridge_set_trait(self, id, trait_name, value):
        """ Set a trait on the model. """

        value = json.loads(value)
        obj = self._id_to_object_map.get(id)
        try:
            index = int(trait_name)
            obj[index] = value

        except:
            setattr(obj, trait_name, value)

        return

    def _get_type_and_value(self, value):
        """ Return a tuple of the form (type, value) for the value.

        `type` is one of "instance", "list" and "primitive" depending
        on the trait type of value.
        """

        if isinstance(value, HasTraits):
            value_id                         = str(id(value))
            self._id_to_object_map[value_id] = value

            type  = 'instance'
            value = value_id

        elif isinstance(value, list):
            value_id                         = str(id(value))
            self._id_to_object_map[value_id] = value

            type = 'list'
            value = value_id

        else:
            type = 'primitive'

        return type, value

    #### Trait change handlers ################################################

    def _on_model_trait_changed(self, model, trait_name, old, new):
        """ Called when any trait on the model has been changed. """

        print "on model changed", model, trait_name, old, new
        if isinstance(new, TraitListEvent):
            trait_name = trait_name[:-len('_items')]
            value = getattr(model, trait_name)

        else:
            value = new
            if isinstance(value, HasTraits):
                self._id_to_object_map[str(id(value))] = value

            elif isinstance(value, list):
                self._id_to_object_map[str(id(value))] = value

        type, value = self._get_type_and_value(value)

        js = Template("""
        jigna.proxy_manager.on_model_changed('${type}', ${value});
        """).render(
            type   = type,
            value  = repr(value)
        )

        self._widget.execute_js(js)

        return

#### EOF ######################################################################
