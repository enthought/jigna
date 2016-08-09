#
# (C) Copyright 2013-2016 Enthought, Inc., Austin, TX
# All right reserved.
#
""" Abstract base classes for the Jigna server and bridge. """


# Standard library.
import inspect
import json
import logging
import traceback

# Enthought library.
from traits.api import (
    Any, Dict, Event, HasTraits, Instance, Property, Str, TraitDictEvent,
    TraitListEvent
)

# Logging.
logger = logging.getLogger(__name__)


class Bridge(HasTraits):
    """ Bridge that handles the client-server communication. """

    #### 'Bridge' protocol ####################################################

    def send_event(self, event):
        """ Send an event. """

        raise NotImplementedError


class Server(HasTraits):
    """ Server that serves a Jigna view. """

    #### 'Server' protocol ####################################################

    #: Base url for serving content.
    base_url = Property(Str, depends_on='_base_url')
    def _get_base_url(self):
        if not self._base_url.endswith('/'):
            base_url = self._base_url + '/'
        else:
            base_url = self._base_url

        return base_url

    def _set_base_url(self, base_url):
        self._base_url = base_url

    #: URL for the main home page
    home_url = Str('http://root.jigna/index.html')

    #: The html to serve.
    html = Str

    #: The trait change dispatch mechanism to use when traits change.
    trait_change_dispatch = Str('ui')

    #: Context mapping from object name to obj.
    context = Dict
    def _context_changed(self):
        self._register_objects(self.context)

    def _context_items_changed(self, dict_event):
        context = dict(dict_event.added)
        context.update(dict_event.changed)

        self._register_objects(context)

        self._send_context_updated_event(context)

        return

    def send_event(self, event):
        """ Send an event to the client(s). """

        self._bridge.send_event(event)

        return

    def handle_request(self, jsonized_request):
        """ Handle a jsonized request from a client. """

        request = json.loads(jsonized_request)

        # To dispatch the request we have a method named after each one!
        method    = getattr(self, request['kind'])
        exception = None
        try:
            result = method(request)

        except:
            exception = traceback.format_exc()
            logger.exception(exception)
            result = None

        response = dict(exception=exception, result=result)

        return json.dumps(response, default=lambda obj: repr(type(obj)));

    def shutdown(self):
        """ Shutdown the server.

        This unhooks the listeners to trait change events on any objects
        that we know about.

        """

        for obj in self._id_to_object_map.values():
            if isinstance(obj, HasTraits):
                obj.on_trait_change(
                    self._send_object_changed_event, remove=True
                )

    #### Handlers for each kind of request ####################################

    def update_context(self, request):
        """ Update the context on the JS side """
        # This method is called on a page reload or if a new client is used.
        # In these cases, the visited_type_names is no longer relevant as the
        # new client does not have the required data, so clear it.
        self._visited_type_names = set()
        return self._send_context_updated_event(self.context)

    def print_JS_message(self, request):
        """ Prints a message coming from the JS client for testing purposes """

        print('JS: ' + str(request['value']))

        return

    #### Instances ####

    def call_instance_method(self, request):
        """ Call a method on an instance. """

        obj         = self._id_to_object_map[request['id']]
        method_name = request['method_name']
        args        = self._unmarshal_all(request['args'])
        method      = getattr(obj, method_name)

        return self._marshal(method(*args))

    def call_instance_method_thread(self, request):
        """ Call a method on an instance *in a new thread*.

        Return the Id of a Future object which finishes when the method in
        thread finishes.

        """

        obj         = self._id_to_object_map[request['id']]
        method_name = request['method_name']
        args        = self._unmarshal_all(request['args'])
        method      = getattr(obj, method_name)

        from jigna.core.concurrent import Future
        future = Future(
            method, args=tuple(args), dispatch=self.trait_change_dispatch
        )

        def _on_done(result):
            event = dict(
                obj  = str(id(future)),
                name = 'done',
                data = result
            )
            self.send_event(event)

        def _on_error(error):
            error_msg = ''.join(traceback.format_exception(*error))

            logger.error(error_msg)

            event = dict(
                obj  = str(id(future)),
                name = 'error',
                data = error_msg
            )
            self.send_event(event)

        future.on_done(_on_done)
        future.on_error(_on_error)

        return self._marshal(id(future))

    def get_instance_attribute(self, request):
        """ Get the value of an instance attribute. """

        obj            = self._id_to_object_map[request['id']]
        attribute_name = request['attribute_name']

        return self._marshal(getattr(obj, attribute_name))

    def set_instance_attribute(self, request):
        """ Set an attribute on an instance. """

        obj            = self._id_to_object_map[request['id']]
        attribute_name = request['attribute_name']
        value          = self._unmarshal(request['value']);

        setattr(obj, attribute_name, value)

        return

    #### Lists/Dicts ####

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

    #### Private protocol #####################################################

    #: Shadow trait for `base_url`
    _base_url = Str

    #: The bridge that provides the communication between Python and JS.
    _bridge = Instance(Bridge)

    #: All instances, lists and dicts that have been accessed via the bridge.
    #:
    #: { str id : instance_list_or_dict obj }
    _id_to_object_map = Any
    def __id_to_object_map_default(self):
        return {}

    #: The typenames of the Python types that we have already visited.
    #:
    #: And by 'visited' we mean, those types that we have already sent the
    #: the full info for over to the client side.
    _visited_type_names = Any
    def __visited_type_names_default(self):
        return set()

    def _context_ids(self, context):
        """ Return a dictionary keyed with object ids of the objects in
        self._context and whose values are the object ids.
        """
        context_ids = {}
        for obj_name, obj in context.items():
            context_ids[obj_name] = self._marshal(obj)

        return context_ids

    def _get_attribute_names(self, obj):
        """ Get the names of all 'public' attributes on an object.

        Return a list of strings.

        """

        if isinstance(obj, HasTraits):
            attribute_names = [
                name for name in obj.editable_traits()

                if not name.startswith('_')
            ]
        else:
            attribute_names = [
                name for name, value in inspect.getmembers(obj)

                if not inspect.ismethod(value) and not name.startswith('_')
            ]

        return attribute_names

    def _get_dict_info(self, obj):
        """ Get a description of a dict. """

        return dict(keys=list(obj.keys()))

    def _get_event_names(self, obj):
        """ Get the names of all the attributes on an object.

        Return a list of strings.

        """

        # We ignore these triats that are added by the trait machinery :)
        ignore = ['trait_added', 'trait_modified']

        event_names = []

        if isinstance(obj, HasTraits):
            for trait_name in obj.class_trait_names():
                if obj.trait(trait_name).is_trait_type(Event):
                    if trait_name not in ignore:
                        event_names.append(trait_name)

        return event_names

    def _get_instance_info(self, obj):
        """ Get a description of an instance. """

        type_name = self._get_type_name(obj)

        # The first time we send the details of a type over to the client we
        # need to include the full info for it (its attributes, events and
        # methods etc)...
        if type_name not in self._visited_type_names:
            info = dict(
                type_name       = type_name,
                attribute_names = self._get_attribute_names(obj),
                event_names     = self._get_event_names(obj),
                method_names    = self._get_public_method_names(type(obj))
            )
            self._visited_type_names.add(type_name)

        # ... for subsequent calls, we only need to send the type name as the
        # the client will have already built a prototype based on the previous
        # info.
        else:
            info = dict(type_name = type_name)

        return info

    def _get_list_info(self, obj):
        """ Get a description of a list. """

        return dict(length=len(obj))

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

    def _get_type_name(self, obj):
        t = type(obj)
        return t.__module__ + '.' + t.__name__

    def _marshal(self, obj):
        """ Marshal a value. """

        if isinstance(obj, list):
            obj_id = str(id(obj))
            self._id_to_object_map[obj_id] = obj

            type  = 'list'
            value = obj_id
            info  = self._get_list_info(obj)

        elif isinstance(obj, dict):
            obj_id = str(id(obj))
            self._id_to_object_map[obj_id] = obj

            type  = 'dict'
            value = obj_id
            info  = self._get_dict_info(obj)

        # fixme: Not quite right as this will be True for classes too ;^)
        # The intent is to get objects that are non-scalar eg. int, float
        # complex, str etc.
        elif hasattr(obj, '__dict__'):
            obj_id = str(id(obj))
            self._id_to_object_map[obj_id] = obj

            type  = 'instance'
            value = obj_id
            info  = self._get_instance_info(obj)

            if isinstance(obj, HasTraits):
                obj.on_trait_change(
                    self._send_object_changed_event,
                    dispatch=self.trait_change_dispatch
                )
        else:
            type  = 'primitive'
            value = obj
            info  = None

        return dict(type=type, value=value, info=info)

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

    def _register_object(self, obj):
        """ Register the given object with the server. """

        self._id_to_object_map[str(id(obj))] = obj

        return

    def _register_objects(self, objs):
        """ Register more than one objects """

        for obj_name, obj in objs.items():
            self._register_object(obj)

        return

    def _send_object_changed_event(self, obj, trait_name, old, new):
        """ Send an object changed event. """

        if trait_name.startswith('_'):
            return

        if isinstance(new, (TraitListEvent, TraitDictEvent)):
            trait_name  = trait_name[:-len('_items')]
            new         = getattr(obj, trait_name)
            items_event = True

        else:
            # fixme: intent is non-scalar or maybe container?
            if hasattr(new, '__dict__') or isinstance(new, (dict, list)):
                self._register_object(new)

            items_event = False

        event = dict(
            obj  = str(id(obj)),
            name = trait_name,
            # fixme: This smells a bit, but marshalling the new value gives us
            # a type/value pair which we need on the client side to determine
            # what (if any) proxy we need to create.
            data = self._marshal(new),

            # fixme: This is how we currently detect an 'xxx_items' event on
            # the JS side.
            items_event = items_event
        )

        self.send_event(event)

        return

    def _send_context_updated_event(self, context):
        """ Send a context_updated event. """

        event = dict(
            obj  = 'jigna',
            name = 'context_updated',
            data = self._context_ids(context)
        )

        self.send_event(event)

        return

#### EOF ######################################################################
