#
# Enthought product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#


# Standard library.
import inspect
import json
import os
import sys
from os.path import abspath, dirname, join

# 3rd party library.
from jinja2 import Template

# Enthought library.
from traits.api import (
    Any, Dict, HasTraits, Instance, Property, Str, TraitInstance, TraitListEvent
)

# Jigna libary.
from jigna.core.html_widget import HTMLWidget
from jigna.core.wsgi import FileLoader


#### HTML templates ###########################################################

DOCUMENT_HTML_TEMPLATE = """
<html ng-app>
  <head>
      <script type="text/javascript" src="{{jquery}}"></script>
      <script type="text/javascript" src="{{angular}}"></script>
      <script type="text/javascript" src="{{jigna}}"></script>
      <script type="text/javascript">
        $(document).ready(function(){
          jigna.bridge.initialize('{{model_name}}', '{{id}}');
        });
      </script>


      {{head_html}}
  </head>

  <body>
    {{body_html}}
  </body>
</html>
"""


class Bridge(HasTraits):
    """ Bridge between AngularJS and Python worlds. """

    #### 'Bridge' protocol ####################################################

    #: The underlying toolkit control that renders HTML.
    control = Property(Any)
    def _get_control(self):
        return self._widget.control

    def call_method(self, id, method_name, *args, **kw):
        """ Call a method on a registered object. """

        try:
            obj    = self._id_to_object_map.get(id)
            method = getattr(obj, method_name)
            value  = method(*args, **kw)

            exception = None
            type, value = self._get_type_and_value(value)

        except Exception, e:
            exception = repr(sys.exc_type)
            type      = 'exception'
            value     = repr(sys.exc_value)

        return dict(exception=exception, type=type, value=value)

    def get_instance_info(self, id):
        """ Return a description of an instance. """

        obj = self._id_to_object_map.get(id)
        self.register_object(obj)

        info = {
            'trait_names'  : obj.editable_traits(),
            'method_names' : self._get_public_method_names(type(obj))
        }

        return json.dumps(info)

    def get_list_info(self, id):
        """ Returns a description of a list. """

        obj = self._id_to_object_map.get(id)

        return len(obj)

    def get_list_item(self, obj_id, index):
        """ Return the value of a list item. """

        try:
            obj   = self._id_to_object_map.get(obj_id)
            value = obj[int(index)]

            exception = None
            type, value = self._get_type_and_value(value)

        except Exception, e:
            exception = repr(sys.exc_type)
            type      = 'exception'
            value     = repr(sys.exc_value)

        return dict(exception=exception, type=type, value=value)

    def get_trait(self, obj_id, trait_name):
        """ Return the value of a trait on an object. """

        try:
            obj   = self._id_to_object_map.get(obj_id)
            value = getattr(obj, trait_name)

            exception = None
            type, value = self._get_type_and_value(value)

        except Exception, e:
            exception = repr(sys.exc_type)
            type      = 'exception'
            value     = repr(sys.exc_value)

        return json.dumps(dict(exception=exception, type=type, value=value))

    def load_html(self, html, base_url):
        """ Load the given HTML into the bridge. """

        self._widget.load_html(html, base_url)

        return

    def on_object_changed(self, type, value):
        """ Let the JS-side know that a trait has changed. """

        js = Template("""
            jigna.bridge.on_object_changed('{{type}}', {{value}});
        """).render(
            type   = type,
            value  = repr(value)
        )

        self._widget.execute_js(js)

        return

    def register_object(self, obj):
        """ Register the given object with the bridge. """

        self._id_to_object_map[str(id(obj))] = obj
        obj.on_trait_change(self._on_object_trait_changed)

        return

    def set_list_item(self, id, index, value):
        """ Set an item in a list. """

        obj   = self._id_to_object_map.get(id)
        value = json.loads(value)

        # fixme: index should be an int already!
        obj[int(index)] = value

        # fixme: return result? exceptions?
        return

    def set_trait(self, id, trait_name, value):
        """ Set a trait on an object. """

        obj   = self._id_to_object_map.get(id)
        value = json.loads(value)

        setattr(obj, trait_name, value)

        # fixme: return result? exceptions?
        return

    #### Private protocol #####################################################

    #: All instance and lists that have been accessed via the bridge.
    #:
    #: { str id : instance_or_list obj }
    _id_to_object_map = Dict

    #: The toolkit-specific widget that renders the HTML.
    _widget = Any
    def __widget_default(self):
        return self._create_widget()

    def _create_widget(self):
        """ Create the HTML widget that we use to render the view. """

        hosts = {
            'resources.jigna': FileLoader(
                root = join(abspath(dirname(__file__)), 'resources')
            )
        }

        widget = HTMLWidget(
            callbacks        = [
                ('call_method',       self.call_method),
                ('get_instance_info', self.get_instance_info),
                ('get_trait',         self.get_trait),
                ('set_trait',         self.set_trait),
                ('get_list_info',     self.get_list_info),
                ('get_list_item',     self.get_list_item),
                ('set_list_item',     self.set_list_item),
            ],
            python_namespace = 'python_bridge',
            hosts            = hosts,
            open_externally  = True,
            debug            = True
        )
        widget.create()

        return widget

    def _get_public_method_names(self, cls):
        """ Get the names of all public methods on a class.

        Return a list of strings.

        """

        public_methods = []
        for c in inspect.getmro(cls):
            if c is HasTraits:
                break

            for name in c.__dict__:
                if not name.startswith( '_' ):
                    value = getattr(c, name)
                    if inspect.ismethod(value):
                        public_methods.append(name)

        return public_methods

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
        self.on_object_changed(type, value)

        return


class JignaView(HasTraits):
    """ A factory for HTML/AngularJS based user interfaces. """

    MODEL_NAME = 'model'

    #### 'JignaView' protocol #################################################

    #: The HTML for the *body* of the view's document.
    body_html = Str

    #: The HTML for the *head* of the view's document.
    head_html = Str

    #: The base url for all the resources.
    base_url = Property(Str)
    _base_url = Str
    def _get_base_url(self):
        return self._base_url

    def _set_base_url(self, url):
        self._base_url = join(os.getcwd(), url)

    def __base_url_default(self):
        return os.getcwd()

    def show(self, model):
        """ Create and show a view of the given model. """

        self._bridge = Bridge()
        self._bridge.load_html(self._generate_html(model), self.base_url)
        self._bridge.register_object(model)
        self._bridge.control.show()

        return

    #### Private protocol #####################################################

    def _generate_html(self, model):
        """ Generate the HTML document with the given model. """

        template = Template(DOCUMENT_HTML_TEMPLATE)
        html     = template.render(
            jquery     = 'http://resources.jigna/js/jquery.min.js',
            angular    = 'http://resources.jigna/js/angular.min.js',
            jigna      = 'http://resources.jigna/js/jigna.js',
            model_name = JignaView.MODEL_NAME,
            id         = id(model),
            body_html  = self.body_html,
            head_html  = self.head_html
        )

        return html

#### EOF ######################################################################
