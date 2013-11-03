//
// Enthought product code
//
// (C) Copyright 2013 Enthought, Inc., Austin, TX
// All right reserved.
//
// This file is confidential and NOT open source.  Do not distribute.
//

// Namespace for all Jigna-related objects.
var jigna = {};

jigna.initialize = function(model_name, id) {
    jigna.bridge = new jigna.Bridge();
    jigna.broker = new jigna.Broker(model_name, id);
};

///////////////////////////////////////////////////////////////////////////////
// Bridge
///////////////////////////////////////////////////////////////////////////////

jigna.Bridge = function() {
    // Private protocol
    this._python = window['python'];
};

jigna.Bridge.prototype.recv = function(jsonized_request) {
    /* Handle a request from the Python-side. */

    var jsonized_response, request, response;

    request           = JSON.parse(jsonized_request);
    response          = jigna.broker.handle_request(request)
    jsonized_response = JSON.stringify(response);

    return jsonized_response;
};

jigna.Bridge.prototype.send = function(request) {
    /* Send a request to the Python-side. */

    var jsonized_request, jsonized_response, response;

    jsonized_request  = JSON.stringify(request);
    jsonized_response = this._python.recv(jsonized_request);
    response          = JSON.parse(jsonized_response);

    return response;
};

///////////////////////////////////////////////////////////////////////////////
// Broker
///////////////////////////////////////////////////////////////////////////////

jigna.Broker = function(model_name, id) {
    // Private protocol
    this._id_to_proxy_map = {};
    this._proxy_factory   = new jigna.ProxyFactory(this);
    this._scope           = $(document.body).scope();

    // Add the model.
    this.add_model(model_name, id);
};

jigna.Broker.prototype.add_model = function(model_name, id) {
    var proxy, scope;

    // Get a proxy for the object identified by Id...
    proxy = this._create_proxy('instance', id);

    // ... and expose it with the name 'model_name' to AngularJS.
    scope = this._scope;
    scope.$apply(function() {scope[model_name] = proxy;});
};

// Not sure we need hanlde_request this side... since we only actually
// take events and in WebSocket world that its one way (ie. no return value).
jigna.Broker.prototype.on_object_changed = function(event) {
    this._create_proxy(event.type, event.value);

    if (this._scope.$$phase === null){
        this._scope.$digest();
    };
};

jigna.Broker.prototype.handle_request = function(request) {
    /* Handle a request from the Python-side. */

    var args, exception, method, value;
    try {
        method    = this[request.method_name];
        // fixme: We need type in the event to know what kind of proxy to create
        //args      = this._unmarshal_all(request.args);
        args      = request.args;
        value     = method.apply(this, args);
        exception = null;
    }
    catch (error) {
        exception = error;
        value     = error.message;
    };

    response = {'exception' : exception, 'result' : this._marshal(value)};
    return response;
};

jigna.Broker.prototype.send_request = function(method_name, args) {
    /* Send a request to the Python-side. */

    var request, response;

    request  = {'method_name' : method_name, 'args' : this._marshal_all(args)};
    response = jigna.bridge.send(request);
    result   = this._unmarshal(response.result);

    if (response.exception !== null) {
        throw result;
    }

    return result;
};

// Private protocol //////////////////////////////////////////////////////////

jigna.Broker.prototype._create_proxy = function(type, obj) {
    var proxy;
    if (type === 'primitive') {
        proxy = obj;
    }
    else {
        proxy = this._proxy_factory.create_proxy(type, obj);
        this._id_to_proxy_map[obj] = proxy;
    };

    return proxy;
};

jigna.Broker.prototype._marshal = function(obj) {
    var type, value;

    if (obj === null || obj === undefined || obj.__id__ === undefined) {
        type  = 'primitive';
        value = obj;

    } else {
        // fixme: Or list!
        type  = 'instance';
        value = obj.__id__;
    };

    return {'type' : type, 'value' : value};
};

jigna.Broker.prototype._marshal_all = function(objs) {
    var index;

    for (index in objs) {
        objs[index] = this._marshal(objs[index]);
    };

    // For convenience, as we modify the array in-place.
    return objs;
};

jigna.Broker.prototype._unmarshal = function(obj) {
    var value;

    if (obj.type === 'primitive') {
        value = obj.value;

    } else {
        value = this._id_to_proxy_map[obj.value];
        if (value === undefined) {
            value = this._create_proxy(obj.type, obj.value);
        }
    }

    return value;
};

jigna.Broker.prototype._unmarshal_all = function(objs) {
    var index;

    for (index in objs) {
        objs[index] = this._unmarshal(objs[index]);
    };

    // For convenience, as we modify the array in-place.
    return objs;
};

///////////////////////////////////////////////////////////////////////////////
// ProxyFactory
///////////////////////////////////////////////////////////////////////////////

jigna.ProxyFactory = function(broker) {
    // Private protocol.
    this._broker = broker;
};

jigna.ProxyFactory.prototype.create_proxy = function(type, obj) {
    /* Make a proxy for the given value (typed by type!). */

    var proxy;

    if (type === 'instance') {
        proxy = this._create_instance_proxy(obj);
    }
    else if (type === 'list') {
        proxy = this._create_list_proxy(obj);
    }
    else {
        throw 'cannot create proxy for type: ' + type;
    }

    return proxy;
};

// Private protocol //////////////////////////////////////////////////////////

jigna.ProxyFactory.prototype._add_list_item_property = function(proxy, index){
    var get, set;

    get = function() {
        // In here, 'this' refers to the proxy!
        return this.__broker__.send_request('get_list_item', [this, index]);
    };

    set = function(value) {
        // In here, 'this' refers to the proxy!
        this.__broker__.send_request('set_list_item', [this, index, value]);
    };

    this._add_property(proxy, index, get, set);
};

jigna.ProxyFactory.prototype._add_method = function(proxy, method_name){
    var method = function () {
        // In here, 'this' refers to the proxy!
        //
        // In JS, 'arguments' is not a real array, so this converts it to one!
        var args   = Array.prototype.slice.call(arguments);
        var result = this.__broker__.send_request(
            'call_method', [this, method_name].concat(args)
        );

        return result;
    };

    proxy[method_name] = method;
};

jigna.ProxyFactory.prototype._add_property = function(proxy, name, get, set){
    var descriptor = {
        get          : get,
        set          : set,
        configurable : true,
        enumerable   : true,
        writeable    : true
    };

    Object.defineProperty(proxy, name, descriptor);
};

jigna.ProxyFactory.prototype._add_trait_property = function(proxy, trait_name){
    var get = function() {
        // In here, 'this' refers to the proxy!
        return this.__broker__.send_request('get_trait', [this, trait_name]);
    };

    var set = function(value) {
        // In here, 'this' refers to the proxy!
        this.__broker__.send_request('set_trait', [this, trait_name, value]);
    };

    this._add_property(proxy, trait_name, get, set);
};

jigna.ProxyFactory.prototype._create_instance_proxy = function(id) {
    var proxy = new jigna.Proxy(id, this._broker);
    var info = this._broker.send_request('get_instance_info', [proxy]);

    var trait_names = info.trait_names;
    for (var index in trait_names) {
        this._add_trait_property(proxy, trait_names[index]);
    }

    var method_names = info.method_names;
    for (var index in method_names) {
        this._add_method(proxy, method_names[index]);
    }

    return proxy;
};

jigna.ProxyFactory.prototype._create_list_proxy = function(id) {
    var proxy = new jigna.Proxy(id, this._broker);
    var list_length = this._broker.send_request('get_list_info', [proxy]);

    for (var index=0; index < list_length; index++) {
        this._add_list_item_property(proxy, index);
    }

    return proxy;
};

///////////////////////////////////////////////////////////////////////////////
// Proxy
///////////////////////////////////////////////////////////////////////////////

jigna.Proxy = function(id, broker) {
    var descriptor = {configurable:true, enumerable:false, writeable:true};

    descriptor.value = id;
    Object.defineProperty(this, '__id__', descriptor);

    descriptor.value = broker;
    Object.defineProperty(this, '__broker__', descriptor);
};

// EOF ////////////////////////////////////////////////////////////////////////
