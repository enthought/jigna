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

# Enthought library.
from pyface.api import GUI
from traits.api import (
    Any, Dict, HasTraits, Instance, Property, Str,
    TraitDictEvent, TraitDictObject, TraitInstance, TraitListEvent
)

# Jigna libary.
from jigna.core.html_widget import HTMLWidget
from jigna.core.wsgi import FileLoader


#### HTML templates ###########################################################

DOCUMENT_HTML_TEMPLATE = """
<html ng-app='jigna'>
  <head>
    <script type="text/javascript" src="/jigna/js/jquery.min.js"></script>
    <script type="text/javascript" src="/jigna/js/angular.min.js"></script>
    <script type="text/javascript" src="/jigna/js/jigna.js"></script>

    {head_html}

  </head>

  <body>
    {body_html}
  </body>
</html>
"""


class Bridge(HasTraits):
    """ Bridge that handles the client-server communication. """

    #### 'Bridge' protocol ####################################################

    #: The server that we provide the bridge for.
    server = Any

    def send_event(self, event):
        """ Send an event. """

        jsonized_event = json.dumps(event)

        # This looks weird but this is how we fake an event being 'received'
        # on the client side when using the Qt bridge!
        self.widget.execute_js(
            'jigna.client.bridge.handle_event(%r);' % jsonized_event
        )

        return

    def handle_request(self, jsonized_request):
        """ Handle a request from the client. """

        request  = json.loads(jsonized_request)
        response = self.server.handle_request(request)

        def default(obj):
            return repr(type(obj))

        return json.dumps(response, default=default);

    #### 'QtWebKitBridge' protocol ############################################

    #: The 'HTMLWidget' that contains the QtWebLit malarky.
    widget = Any


class Server(HasTraits):
    """ Server that exposes Python objects to JS. """

    #### 'Server' protocol ####################################################

    #: The bridge that provides the communication between Python and JS.
    bridge = Instance(Bridge)
    def _bridge_changed(self, trait_name, old, new):
        if old is not None:
            old.server = None

        if new is not None:
            new.server = self

        return

    #: Base url for serving the html content
    base_url = Str

    #: Context mapping from object name to obj
    context = Dict
    def _context_changed(self):
        self._register_objects(self.context)

    #: The html to serve
    html = Str

    def send_event(self, event):
        """ Send an event to the client(s). """

        self.bridge.send_event(event)

        return

    def handle_request(self, request):
        """ Handle a request from a client. """

        try:
            # To dispatch the request we have a method named after each one!
            method    = getattr(self, request['kind'])
            result    = method(request)
            exception = None

        except Exception, e:
            exception = repr(sys.exc_value)
            result    = None

        return dict(exception=exception, result=result)

    def _register_object(self, obj):
        """ Register the given object with the server. """

        self._id_to_object_map[str(id(obj))] = obj

        return

    def _register_objects(self, objs):
        """ Register more than one objects """

        for obj_name, obj in objs.items():
            self._register_object(obj)

        return

    #### Handlers for each kind of request ####################################

    def get_context(self, request):
        """ Get the models and model names in the context. """

        context_ids = {}
        for obj_name, obj in self.context.items():
            context_ids[obj_name] = str(id(obj))

        return context_ids

    #### Instances ####

    def call_instance_method(self, request):
        """ Call a method on a instance. """

        obj         = self._id_to_object_map[request['id']]
        method_name = request['method_name']
        args        = self._unmarshal_all(request['args'])
        method      = getattr(obj, method_name)

        return self._marshal(method(*args))

    def get_instance_attribute(self, request):
        """ Get the value of an instance attribute. """

        obj            = self._id_to_object_map[request['id']]
        attribute_name = request['attribute_name']

        return self._marshal(getattr(obj, attribute_name))

    def get_instance_info(self, request):
        """ Get a description of an instance. """

        obj = self._id_to_object_map[request['id']]

        if isinstance(obj, HasTraits):
            obj.on_trait_change(self._send_object_changed_event, dispatch='ui')

        info = dict(
            type_name        = type(obj).__module__ + '.' + type(obj).__name__,
            attribute_names  = self._get_public_attribute_names(obj),
            method_names     = self._get_public_method_names(type(obj))
        )

        return info

    def set_instance_attribute(self, request):
        """ Set an attribute on an instance. """

        obj            = self._id_to_object_map[request['id']]
        attribute_name = request['attribute_name']
        value          = self._unmarshal(request['value']);

        setattr(obj, attribute_name, value)

        return

    #### Lists/Dicts ####

    def get_dict_info(self, request):
        """ Get a description of a dict. """

        obj  = self._id_to_object_map[request['id']]
        info = dict(keys=obj.keys())

        return info

    def get_list_info(self, request):
        """ Get a description of a list. """

        obj  = self._id_to_object_map[request['id']]
        info = dict(length=len(obj))

        return info

    def get_item(self, request):
        """ Get the value of an item in a list or dict. """

        obj   = self._id_to_object_map[request['id']]
        index = request['index']

        return self._marshal(obj[index])

    def set_item(self, request):
        """ Set the value of a an item in a list or dict. """

        obj   = self._id_to_object_map[request['id']]
        index = request['index']
        value = self._unmarshal(request['value'])

        obj[index] = value

        return

    #### Dicts ####

    #### Private protocol #####################################################

    #: All instance and lists that have been accessed via the bridge.
    #:
    #: { str id : instance_or_list obj }
    _id_to_object_map = Dict

    def _get_public_attribute_names(self, obj):
        """ Get the names of all public attributes on an object.

        Return a list of strings.

        """

        if isinstance(obj, HasTraits):
            public_attribute_names = [
                name for name in obj.editable_traits()

                if not name.startswith( '_' )
            ]
        else:
            public_attribute_names = [
                name for name, value in inspect.getmembers(obj)

                if not name.startswith('_') and not inspect.ismethod(value)
            ]

        return public_attribute_names

    def _get_public_method_names(self, cls):
        """ Get the names of all public methods on a class.

        Return a list of strings.

        """

        public_method_names = []
        for c in inspect.getmro(cls):
            if c is HasTraits:
                break

            for name in c.__dict__:
                if not name.startswith( '_' ):
                    value = getattr(c, name)
                    if inspect.ismethod(value):
                        public_method_names.append(name)

        return public_method_names

    def _marshal(self, obj):
        """ Marshal a value. """

        if isinstance(obj, list):
            obj_id = str(id(obj))
            self._id_to_object_map[obj_id] = obj

            type  = 'list'
            value = obj_id

        elif isinstance(obj, dict):
            obj_id = str(id(obj))
            self._id_to_object_map[obj_id] = obj

            type  = 'dict'
            value = obj_id

        # fixme: Not quite right as this will be True for classes too ;^)
        # The intent is to get objects that are non-scalar eg. int, float
        # complex, str etc.
        elif hasattr(obj, '__dict__'):
            obj_id = str(id(obj))
            self._id_to_object_map[obj_id] = obj

            type  = 'instance'
            value = obj_id

        else:
            type  = 'primitive'
            value = obj

        return dict(type=type, value=value)

    def _marshal_all(self, iter):
        """ Marshal all of the values in an iterable. """

        return [self._marshal(obj) for obj in iter]

    def _unmarshal(self, obj):
        """ Unmarshal a value. """

        if obj['type'] == 'primitive':
            value = obj['value']

        else:
            value = self._id_to_object_map[obj['value']]

        return value

    def _unmarshal_all(self, iter):
        """ Unmarshal all of the values in an iterable. """

        return [self._unmarshal(obj) for obj in iter]

    def _send_object_changed_event(self, obj, trait_name, old, new):
        """ Send an object changed event. """

        if trait_name.startswith('_'):
            return

        if isinstance(new, (TraitListEvent, TraitDictEvent)):
            trait_name = trait_name[:-len('_items')]
            new        = getattr(obj, trait_name)

        else:
            # fixme: intent is non-scalar or maybe container?
            if hasattr(new, '__dict__') or isinstance(new, (dict, list)):
                self._register_object(new)

        event = dict(
            kind           = 'object_changed',
            obj            = str(id(obj)),
            attribute_name = trait_name,
            # fixme: This smells a bit, but marhsalling the new value gives us
            # a type/value pair which we need on the client side to determine
            # what (if any) proxy we need to create.
            new_obj        = self._marshal(new)
        )

        self.send_event(event)

        return


class View(HasTraits):
    """ A factory for HTML/AngularJS based user interfaces. """

    ### 'View' class protocol #################################################

    @classmethod
    def from_file(cls, html_file):
        with open(html_file, 'rb') as f:
            html = f.read()

        return cls(html=html)

    #### 'View' protocol ######################################################

    #: The base url for all resources.
    base_url = Str
    def _base_url_default(self):
        return os.getcwd()

    #: The HTML for the *body* of the view's document.
    body_html = Str

    #: The underlying toolkit control that renders HTML.
    control = Property(Any)
    def _get_control(self):
        return self._widget.control

    #: The HTML for the *head* of the view's document.
    head_html = Str

    #: The HTML for the entire document.
    html = Str
    def _html_default(self):
        """ Get the default HTML document for the given model. """

        html     = DOCUMENT_HTML_TEMPLATE.format(
            body_html  = self.body_html,
            head_html  = self.head_html
        )

        return html

    def show(self, **context):
        """ Create and show a view of the given context. """

        self._server = Server(
            html=self.html,
            base_url=self.base_url,
            bridge=Bridge(widget=self._widget), 
            context=context
        )
        self.control.loadFinished.connect(self._on_load_finished)
        self._load_html(self.html, self.base_url)
        self.control.show()

        return

    #### Private protocol #####################################################

    #: The server that manages the objects shared via the bridge.
    _server = Instance(Server)

    #: The toolkit-specific widget that renders the HTML.
    _widget = Any
    def __widget_default(self):
        return self._create_widget()

    def _create_widget(self):
        """ Create the HTML widget that we use to render the view. """

        root_paths = {
            'jigna': FileLoader(
                root = join(abspath(dirname(__file__)), 'resources')
            )
        }

        widget = HTMLWidget(
            callbacks        = [('handle_request', self._handle_request)],
            python_namespace = 'qt_bridge',
            root_paths       = root_paths,
            open_externally  = True,
            debug            = True
        )
        widget.create()

        return widget

    def _handle_request(self, request):
        """ Handle a request from a client. """

        return self._server.bridge.handle_request(request)

    def _load_html(self, html, base_url):
        """ Load the given HTML into the widget.

        This call blocks until the document had loaded.

        """

        self._load_finished = False

        self._widget.load_html(html, base_url)

        while not self._load_finished:
            GUI.process_events()

        return

    def _on_load_finished(self):
        """ Called when the HTML document has finished loading. """

        self._load_finished = True

        return

#### EOF ######################################################################
