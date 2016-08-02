///////////////////////////////////////////////////////////////////////////////
// Client
///////////////////////////////////////////////////////////////////////////////

jigna.Client = function() {};

jigna.Client.prototype.initialize = function() {
    // jigna.Client protocol.
    this.bridge           = this._get_bridge();

    // Private protocol.
    this._id_to_proxy_map = {};
    this._proxy_factory   = this._create_proxy_factory();

    // Add all of the models being edited
    jigna.add_listener(
        'jigna',
        'context_updated',
        function(event){this._add_models(event.data);},
        this
    );

    // Wait for the bridge to be ready, and when it is ready, update the
    // context so that initial models are added to jigna scope
    var client = this;
    this.bridge.ready.done(function(){
        client.update_context();
    });
};

jigna.Client.prototype.handle_event = function(jsonized_event) {
    /* Handle an event from the server. */
    var event = JSON.parse(jsonized_event);
    jigna.fire_event(event.obj, event);
};

jigna.Client.prototype.on_object_changed = function(event){
    if (jigna.debug) {
        this.print_JS_message('------------on_object_changed--------------');
        this.print_JS_message('object id  : ' + event.obj);
        this.print_JS_message('attribute  : ' + event.name);
        this.print_JS_message('items event: ' + event.items_event);
        this.print_JS_message('new type   : ' + event.data.type);
        this.print_JS_message('new value  : ' + event.data.value);
        this.print_JS_message('new info   : ' + event.data.info);
        this.print_JS_message('-------------------------------------------');
    }

    var proxy = this._id_to_proxy_map[event.obj];

    // If the *contents* of a list/dict have changed then we need to update
    // the associated proxy to reflect the change.
    if (event.items_event) {
        var collection_proxy = this._id_to_proxy_map[event.data.value];
        // The collection proxy can be undefined if on the Python side you
        // have re-initialized a list/dict with the same value that it
        // previously had, e.g.
        //
        // class Person(HasTraits):
        //     friends = List([1, 2, 3])
        //
        // fred = Person()
        // fred.friends = [1, 2, 3] # No trait changed event!!
        //
        // This is because even though traits does copy on assignment for
        // lists/dicts (and hence the new list will have a new Id), it fires
        // the trait change events only if it considers the old and new values
        // to be different (ie. if does not compare the identity of the lists).
        //
        // For us(!), it means that we won't have seen the new list before we
        // get an items changed event on it.
        if (collection_proxy === undefined) {
            proxy.__cache__[event.name] = this._create_proxy(
                event.data.type, event.data.value, event.data.info
            );

        } else {
            this._proxy_factory.update_proxy(
                collection_proxy, event.data.type, event.data.info
            );
        }

    } else {
        proxy.__cache__[event.name] = this._unmarshal(event.data);
    }

    // Angular listens to this event and forces a digest cycle which is how it
    // detects changes in its watchers.
    jigna.fire_event('jigna', {name: 'object_changed', object: proxy});
};

jigna.Client.prototype.send_request = function(request) {
    /* Send a request to the server and wait for (and return) the response. */

    var jsonized_request  = JSON.stringify(request);
    var jsonized_response = this.bridge.send_request(jsonized_request);

    return JSON.parse(jsonized_response).result;
};

// Convenience methods for each kind of request //////////////////////////////

jigna.Client.prototype.call_instance_method = function(id, method_name, args) {
    /* Call an instance method */

    var request = {
        kind        : 'call_instance_method',
        id          : id,
        method_name : method_name,
        args        : this._marshal_all(args)
    };

    var response = this.send_request(request);
    var result = this._unmarshal(response);

    return result;
};

jigna.Client.prototype.call_instance_method_thread = function(id, method_name, args) {
    /* Call an instance method in a thread. Useful if the method takes long to
    execute and you don't want to block the UI during that time.*/

    var request = {
        kind        : 'call_instance_method_thread',
        id          : id,
        method_name : method_name,
        args        : this._marshal_all(args),
    };

    // the response of a threaded request is a marshalled version of a python
    // future object. We attach 'done' and 'error' handlers on that object to
    // resolve/reject our own deferred.
    var response = this.send_request(request);
    var future_obj = this._unmarshal(response);

    var deferred = new $.Deferred();

    jigna.add_listener(future_obj, 'done', function(event){
        deferred.resolve(event.data);
    });

    jigna.add_listener(future_obj, 'error', function(event){
        deferred.reject(event.data);
    });

    return deferred.promise();
};

jigna.Client.prototype.get_attribute = function(proxy, attribute) {
    /* Get the specified attribute of the proxy from the server. */

    var request = this._create_request(proxy, attribute);

    var response = this.send_request(request);
    var result = this._unmarshal(response);

    return result;
};

jigna.Client.prototype.print_JS_message = function(message) {
    var request = {
        kind: 'print_JS_message',
        value: message
    };

    this.send_request(request);
};

jigna.Client.prototype.set_instance_attribute = function(id, attribute_name, value) {
    var request = {
        kind           : 'set_instance_attribute',
        id             : id,
        attribute_name : attribute_name,
        value          : this._marshal(value)
    };

    this.send_request(request);
};

jigna.Client.prototype.set_item = function(id, index, value) {
    var request = {
        kind  : 'set_item',
        id    : id,
        index : index,
        value : this._marshal(value)
    };

    this.send_request(request);
};

jigna.Client.prototype.update_context = function() {
    var request  = {kind : 'update_context'};

    this.send_request(request);
};

// Private protocol //////////////////////////////////////////////////////////

jigna.Client.prototype._add_model = function(model_name, id, info) {
    // Create a proxy for the object identified by the Id...
    var proxy = this._create_proxy('instance', id, info);

    // fire the event to let the UI toolkit know that a new model was added
    var data = {};
    data[model_name] = proxy;

    jigna.fire_event('jigna', {
        name: 'model_added',
        data: data,
    });

    return proxy;
};

jigna.Client.prototype._add_models = function(context) {
    var client = this;
    var models = {};
    $.each(context, function(model_name, model) {
        if (jigna.models[model_name] === undefined) {
            proxy = client._add_model(model_name, model.value, model.info);
            models[model_name] = proxy;
        }
    });

    // Resolve the jigna.ready deferred, at this point the initial set of
    // models are set.  For example vue.js can now use these data models to
    // create the initial Vue instance.
    jigna.ready.resolve();

    return models;
};

jigna.Client.prototype._create_proxy_factory = function() {
    return new jigna.ProxyFactory(this);
};

jigna.Client.prototype._create_proxy = function(type, obj, info) {
    if (type === 'primitive') {
        return obj;
    }
    else {
        var proxy = this._proxy_factory.create_proxy(type, obj, info);
        this._id_to_proxy_map[obj] = proxy;
        return proxy;
    }
};

jigna.Client.prototype._create_request = function(proxy, attribute) {
    /* Create the request object for getting the given attribute of the proxy. */

    var request;
    if (proxy.__type__ === 'instance') {
        request = {
            kind           : 'get_instance_attribute',
            id             : proxy.__id__,
            attribute_name : attribute
        };
    }
    else if ((proxy.__type__ === 'list') || (proxy.__type__ === 'dict')) {
        request = {
            kind  : 'get_item',
            id    : proxy.__id__,
            index : attribute
        };
    }
    return request;
};

jigna.Client.prototype._get_bridge = function() {
    var bridge, qt_bridge;

    // Are we using the intra-process Qt Bridge...
    qt_bridge = window['qt_bridge'];
    if (qt_bridge !== undefined) {
        bridge = new jigna.QtBridge(this, qt_bridge);
    // ... or the inter-process web bridge?
    } else {
        bridge = new jigna.WebBridge(this);
    }

    return bridge;
};

jigna.Client.prototype._marshal = function(obj) {
    var type, value;

    if (obj instanceof jigna.Proxy) {
        type  = obj.__type__;
        value = obj.__id__;

    } else {
        type  = 'primitive';
        value = obj;
    }

    return {'type' : type, 'value' : value};
};

jigna.Client.prototype._marshal_all = function(objs) {
    var index;

    for (index in objs) {
        objs[index] = this._marshal(objs[index]);
    }

    // For convenience, as we modify the array in-place.
    return objs;
};

jigna.Client.prototype._unmarshal = function(obj) {

    if (obj === null) {
        return null;
    }

    if (obj.type === 'primitive') {
        return obj.value;

    } else {
        value = this._id_to_proxy_map[obj.value];
        if (value === undefined) {
            return this._create_proxy(obj.type, obj.value, obj.info);
        }
        else {
            return value;
        }
    }
};
