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

        self._register_object(model)

        self._widget = self._create_widget(model)
        self._widget.control.show()

        return

    #### Private protocol #####################################################

    #: All instance and lists that have been accessed via the bridge.
    #:
    #: { str id : instance_or_list obj }
    _id_to_object_map = Dict

    def _register_object(self, obj):
        """ Register the given object with the bridge. """

        self._id_to_object_map[str(id(obj))] = obj
        obj.on_trait_change(self._on_object_trait_changed)

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
                ('get_trait',         self._bridge_get_trait),
                ('set_trait',         self._bridge_set_trait),
                ('get_list_info',     self._bridge_get_list_info),
                ('get_list_item',     self._bridge_get_list_item),
                ('set_list_item',     self._bridge_set_list_item),
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
        self._register_object(obj)

        return obj.editable_traits()

    def _bridge_get_list_info(self, id):
        """ Returns a description of a list. """

        obj = self._id_to_object_map.get(id)

        return len(obj)

    def _bridge_get_list_item(self, obj_id, index):
        """ Return the value of a list item. """

        try:
            obj   = self._id_to_object_map.get(obj_id)
            value = obj[int(index)]

            exception = None
            type, value = self._get_type_and_value(value)

        except Exception, e:
            exception = repr(sys.exc_type),
            type      = 'exception',
            value     = repr(sys.exc_value)

        return dict(exception=None, type=type, value=value)

    def _bridge_get_trait(self, obj_id, trait_name):
        """ Return the value of a trait on an object. """

        try:
            obj   = self._id_to_object_map.get(obj_id)
            value = getattr(obj, trait_name)

            exception = None,
            type, value = self._get_type_and_value(value)

        except Exception, e:
            exception = repr(sys.exc_type),
            type      = 'exception',
            value     = repr(sys.exc_value)

        return dict(exception=None, type=type, value=value)

    def _bridge_on_object_changed(self, type, value):
        """ Let the JS-side know that a trait has changed. """

        js = Template("""
            jigna.proxy_manager.on_object_changed('${type}', ${value});
        """).render(
            type   = type,
            value  = repr(value)
        )

        self._widget.execute_js(js)

        return


    def _bridge_set_list_item(self, id, index, value):
        """ Set an item in a list. """

        obj   = self._id_to_object_map.get(id)
        value = json.loads(value)

        # fixme: index should be an int already!
        obj[int(index)] = value

        # fixme: return result? exceptions?
        return

    def _bridge_set_trait(self, id, trait_name, value):
        """ Set a trait on an object. """

        obj   = self._id_to_object_map.get(id)
        value = json.loads(value)

        setattr(obj, trait_name, value)

        # fixme: return result? exceptions?
        return

    def _get_type_and_value(self, value):
        """ Return a tuple of the form (type, value) for the value.

        `type` is either "instance", "list" or "primitive".

        """

        if isinstance(value, HasTraits):
            value_id = str(id(value))
            self._id_to_object_map[value_id] = value

            type  = 'instance'
            value = value_id

        elif isinstance(value, list):
            value_id = str(id(value))
            self._id_to_object_map[value_id] = value

            type = 'list'
            value = value_id

        else:
            type = 'primitive'

        return type, value

    #### Trait change handlers ################################################

    def _on_object_trait_changed(self, obj, trait_name, old, new):
        """ Called when any trait on a registered object has been changed. """

        if isinstance(new, TraitListEvent):
            trait_name = trait_name[:-len('_items')]
            value      = getattr(obj, trait_name)

        else:
            value = new
            if isinstance(value, HasTraits) or isinstance(value, list):
                self._id_to_object_map[str(id(value))] = value

        type, value = self._get_type_and_value(value)
        self._bridge_on_object_changed(type, value)

        return

#### EOF ######################################################################
