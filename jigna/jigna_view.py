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
        jigna.initialize('{{model_name}}', '{{id}}');
      });
    </script>

    {{head_html}}

  </head>

  <body>
    {{body_html}}
  </body>
</html>
"""


class JSError(Exception):
    """ Raised when an exception occurred on the JS-side. """


class Bridge(HasTraits):
    """ Bridge between AngularJS and Python worlds. """

    #### 'Bridge' protocol ####################################################

    broker = Any

    #### 'QtWebKitBridge' protocol ############################################

    widget = Any

    def handle_request(self, jsonized_request):
        """ Handle a request from the JS-side. """

        request = json.loads(jsonized_request)
        try:
            method = getattr(self.broker, request['method_name'])
            value  = method(*request['args'])

            exception   = None
            # fixme: Calling private method!
            type, value = self.broker._get_type_and_value(value)

        except Exception, e:
            exception = repr(sys.exc_type)
            type      = 'exception'
            value     = repr(sys.exc_value)

        response = dict(exception=exception, type=type, value=value)
        return json.dumps(response)

    def send_request(self, request):
        """ Send a request to the JS-side. """

        jsonized_request  = json.dumps(request)
        jsonized_response = self.widget.execute_js(
            'jigna.bridge.handle_request(%r);' % jsonized_request
        )

        response = json.loads(jsonized_response)
        if response['exception'] is not None:
            raise JSError(response['value'])

        return response


class Broker(HasTraits):
    """ Broker that exposes Python objects to JS. """

    #### 'Broker' protocol ####################################################

    #: The bridge that provides the communication between Python and JS.
    bridge = Instance(Bridge)
    def _bridge_changed(self, trait_name, old, new):
        if old is not None:
            old.broker = None

        if new is not None:
            new.broker = self

        return

    def call_method(self, id, method_name, *args):
        """ Call a method on a registered object. """

        obj    = self._id_to_object_map.get(id)
        method = getattr(obj, method_name)
        args   = self._resolve_object_ids(args)

        return method(*args)

    def get_instance_info(self, id):
        """ Return a description of an instance. """

        # fixme: When we register an object, we add it to the id to
        # object map, but it must already be here for this to succeed. It
        # works because we sneakily update the id to object map in the
        # 'Broker._get_type_and_value' method!
        obj = self._id_to_object_map.get(id)
        self.register_object(obj)

        info = {
            'trait_names'  : obj.editable_traits(),
            'method_names' : self._get_public_method_names(type(obj))
        }

        return info

    def get_list_info(self, id):
        """ Returns a description of a list. """

        obj = self._id_to_object_map.get(id)

        return len(obj)

    def get_list_item(self, obj_id, index):
        """ Return the value of a list item. """

        obj = self._id_to_object_map.get(obj_id)

        return obj[int(index)]

    def get_trait(self, obj_id, trait_name):
        """ Return the value of a trait on an object. """

        obj = self._id_to_object_map.get(obj_id)

        return getattr(obj, trait_name)

    def register_object(self, obj):
        """ Register the given object with the broker. """

        self._id_to_object_map[str(id(obj))] = obj
        obj.on_trait_change(self._on_object_trait_changed)

        return

    def set_list_item(self, id, index, value):
        """ Set an item in a list. """

        obj = self._id_to_object_map.get(id)
        obj[index] = value

        return

    def set_trait(self, id, trait_name, value):
        """ Set a trait on an object. """

        obj  = self._id_to_object_map.get(id)
        setattr(obj, trait_name, value)

        return

    #### Private protocol #####################################################

    #: All instance and lists that have been accessed via the bridge.
    #:
    #: { str id : instance_or_list obj }
    _id_to_object_map = Dict

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

            type  = 'list'
            value = value_id

        else:
            type = 'primitive'

        return type, value

    def _resolve_object_ids(self, values):
        """ Resolve any object ids found in the given list of values. """

        actual = []
        for value in values:
            if isinstance(value, dict) and '__id__' in value:
                value = self._id_to_object_map[value['__id__']]

            actual.append(value)

        return actual

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

        event = dict(type=type, value=value)

        request = dict(method_name='on_object_changed', args=(event,))

        self.bridge.send_request(request)

        return


class JignaView(HasTraits):
    """ A factory for HTML/AngularJS based user interfaces. """

    #### 'JignaView' protocol #################################################

    #: The base url for all resources.
    base_url = Property(Str)
    def _get_base_url(self):
        return self._base_url

    def _set_base_url(self, url):
        self._base_url = join(os.getcwd(), url)
        return

    #: The HTML for the *body* of the view's document.
    body_html = Str

    #: The underlying toolkit control that renders HTML.
    control = Property(Any)
    def _get_control(self):
        return self._widget.control

    #: The HTML for the *head* of the view's document.
    head_html = Str

    def show(self, model):
        """ Create and show a view of the given model. """

        self._broker.register_object(model)
        self._load_html(self._get_html(model), self.base_url)
        self.control.show()

        return

    #### Private protocol #####################################################

    #: Shadow trait for the 'base_url'.
    #:
    #: fixme: not sure what this buys us?!?
    _base_url = Str
    def __base_url_default(self):
        return os.getcwd()

    #: The broker that manages the objects shared via the bridge.
    _broker = Instance(Broker)
    def __broker_default(self):
        return Broker(bridge=Bridge(widget=self._widget))

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
            callbacks        = [('handle_request', self._handle_request)],
            python_namespace = 'python',
            hosts            = hosts,
            open_externally  = True,
            debug            = True
        )
        widget.create()

        return widget

    def _handle_request(self, request):
        """ Handle a request from a client. """

        return self._broker.bridge.handle_request(request)

    def _get_html(self, model):
        """ Get the HTML document for the given model. """

        template = Template(DOCUMENT_HTML_TEMPLATE)
        html     = template.render(
            jquery     = 'http://resources.jigna/js/jquery.min.js',
            angular    = 'http://resources.jigna/js/angular.min.js',
            jigna      = 'http://resources.jigna/js/jigna.js',
            model_name = 'model',
            id         = id(model),
            body_html  = self.body_html,
            head_html  = self.head_html
        )

        return html

    def _load_html(self, html, base_url):
        """ Load the given HTML into the widget. """

        self._widget.load_html(html, base_url)

        return

#### EOF ######################################################################
