#
# Enthought product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
""" Abstract base classes for the Jigna server and bridge. """


# Standard library.
import inspect
import json

# Enthought library.
from traits.api import (
    Dict, HasTraits, Instance, Str, TraitDictEvent, TraitListEvent, Event
)


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
    base_url = Str

    #: Context mapping from object name to obj.
    context = Dict
    def _context_changed(self):
        self._register_objects(self.context)
        return

    #: The html to serve.
    html = Str

    #: The trait change dispatch mechanism to use when traits change.
    trait_change_dispatch = Str('ui')

    def send_event(self, event):
        """ Send an event to the client(s). """

        self._bridge.send_event(event)

        return

    def serve(self):
        """ Serve the HTML. """

        raise NotImplementedError

    def handle_request(self, jsonized_request):
        """ Handle a jsonized request from a client. """

        request = json.loads(jsonized_request)
        response = self._handle_request(request)

        def default(obj):
            return repr(type(obj))

        return json.dumps(response, default=default);

    def handle_request_async(self, jsonized_request):
        """ Handle a jsonized request from a client. """
        
        from jigna.core.concurrent import Future

        future = Future(self.handle_request, args=(jsonized_request,),
                        dispatch=self.trait_change_dispatch)
        future_id = self._marshal(future)['value']
        
        def _on_done(result):
            event = dict(type='future_updated', 
                         future_id=future_id,
                         status='done',
                         result=result)
            print "done, send_event:", event
            self.send_event(event)

        def _on_error(error):
            import traceback
            type, value, tb = error
            error_msg = '\n'.join(traceback.format_tb(tb))
            event = dict(type='future_updated', 
                         future_id=future_id,
                         status='error',
                         result=error_msg)
            self.send_event(event)

        future.on_done(_on_done)
        future.on_error(_on_error)

        return future_id


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
        print "calling instance method", method_name

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
            obj.on_trait_change(self._send_object_changed_event,
                                dispatch=self.trait_change_dispatch)

        info = dict(
            type_name        = type(obj).__module__ + '.' + type(obj).__name__,
            attribute_names  = self._get_attribute_names(obj),
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

    #### Private protocol #####################################################

    #: The bridge that provides the communication between Python and JS.
    _bridge = Instance(Bridge)

    #: All instance and lists that have been accessed via the bridge.
    #:
    #: { str id : instance_or_list obj }
    _id_to_object_map = Dict

    def _handle_request(self, request):
        """ Handle a jsonized request from a client. """
        # To dispatch the request we have a method named after each one!
        method    = getattr(self, request['kind'])
        result    = method(request)
        exception = None

        return dict(exception=exception, result=result)

    def _get_attribute_names(self, obj):
        """ Get the names of all the attributes on an object.

        Return a list of strings.

        """

        if isinstance(obj, HasTraits):
            attribute_names = [
                name for name in obj.editable_traits()
            ]
        else:
            attribute_names = [
                name for name, value in inspect.getmembers(obj)

                if not inspect.ismethod(value)
            ]

        return attribute_names

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

        if isinstance(new, (TraitListEvent, TraitDictEvent)):
            trait_name = trait_name[:-len('_items')]
            new        = getattr(obj, trait_name)

        else:
            # fixme: intent is non-scalar or maybe container?
            if hasattr(new, '__dict__') or isinstance(new, (dict, list)):
                self._register_object(new)
        
        if obj.trait(trait_name).is_trait_type(Event):
            event = dict(
                type           = '_event_trait_fired',
                obj            = str(id(obj)),
                attribute_name = trait_name,
                data           = self._marshal(new)
            )

        else:
            event = dict(
                type           = '_object_changed',
                obj            = str(id(obj)),
                attribute_name = trait_name,
                # fixme: This smells a bit, but marhsalling the new value gives us
                # a type/value pair which we need on the client side to determine
                # what (if any) proxy we need to create.
                new_obj        = self._marshal(new)
            )

        self.send_event(event)

        return

#### EOF ######################################################################
