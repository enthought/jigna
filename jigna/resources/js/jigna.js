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
    jigna.bridge = this.create_bridge();
    jigna.broker = new jigna.Broker(model_name, id);
};

jigna.create_bridge = function() {
    var bridge, qt_bridge;

    // Are we using the intra-process Qt Bridge...
    qt_bridge = window['qt_bridge'];
    if (qt_bridge !== undefined) {
        bridge = new jigna.QtBridge(qt_bridge);

    // ... or the inter-process web bridge?
    } else {
        bridge = new jigna.WebBridge();
    }

    return bridge;
};

///////////////////////////////////////////////////////////////////////////////
// QtBridge
///////////////////////////////////////////////////////////////////////////////

jigna.QtBridge = function(qt_bridge) {
    // Private protocol
    this._qt_bridge = qt_bridge;
};

// fixme: duplicated in WebBridge!
jigna.QtBridge.prototype.on_event = function(jsonized_event) {
    /* Handle an event from the server-side. */
    jigna.broker.on_object_changed(JSON.parse(jsonized_event));
};


jigna.QtBridge.prototype.synchronous = function(request) {
    /* Send a request to the server and wait for the reply. */

    var jsonized_request, jsonized_response;

    jsonized_request = JSON.stringify(request);
    jsonized_response = this._qt_bridge.recv(jsonized_request);

    return JSON.parse(jsonized_response);
};

///////////////////////////////////////////////////////////////////////////////
// WebBridge
///////////////////////////////////////////////////////////////////////////////

jigna.WebBridge = function() {
    var url = 'ws://' + window.location.host + '/_jigna_ws';

    this._web_socket = new WebSocket(url);
    this._web_socket.onmessage = function(event) {
        jigna.bridge.on_event(event.data);
    };
};

// fixme: duplicated in Bridge!
jigna.WebBridge.prototype.on_event = function(jsonized_event) {
    /* Handle an event from the server-side. */
    jigna.broker.on_object_changed(JSON.parse(jsonized_event));
};

jigna.WebBridge.prototype.synchronous = function(request) {
    /* Send a request to the server and wait for the reply. */

    var jsonized_request, jsonized_response;

    jsonized_request = JSON.stringify(request);
    $.ajax(
        {
            url     : '/_jigna',
            type    : 'GET',
            data    : {'data': jsonized_request},
            success : function(result) {jsonized_response = result;},
            async   : false
        }
    );

    return JSON.parse(jsonized_response);
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
    this._add_model(model_name, id);
};

jigna.Broker.prototype.on_object_changed = function(event) {
    console.log('on_object_changed', event.type, event.value);
    this._create_proxy(event.type, event.value);

    if (this._scope.$$phase === null){
        this._scope.$digest();
    }
};

jigna.Broker.prototype.invoke_request = function(kind, args) {
    /* Send a request to the server-side and wait for the reply. */

    var request, response, result;

    request  = {'kind' : kind, 'args' : this._marshal_all(args)};
    response = jigna.bridge.synchronous(request);
    result   = this._unmarshal(response.result);

    if (response.exception !== null) {
        throw result;
    }

    return result;
};

// Private protocol //////////////////////////////////////////////////////////

jigna.Broker.prototype._add_model = function(model_name, id) {
    var proxy, scope;

    // Create a proxy for the object identified by the Id...
    proxy = this._create_proxy('instance', id);

    // ... and expose it with the name 'model_name' to AngularJS.
    scope = this._scope;
    scope.$apply(function() {scope[model_name] = proxy;});
};


jigna.Broker.prototype._create_proxy = function(type, obj) {
    var proxy;
    if (type === 'primitive') {
        proxy = obj;
    }
    else {
        proxy = this._proxy_factory.create_proxy(type, obj);
        this._id_to_proxy_map[obj] = proxy;
    }

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
    }

    return {'type' : type, 'value' : value};
};

jigna.Broker.prototype._marshal_all = function(objs) {
    var index;

    for (index in objs) {
        objs[index] = this._marshal(objs[index]);
    }

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
    }

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
        return this.__broker__.invoke_request('get_list_item', [this, index]);
    };

    set = function(value) {
        // In here, 'this' refers to the proxy!
        this.__broker__.invoke_request('set_list_item', [this, index, value]);
    };

    this._add_property(proxy, index, get, set);
};

jigna.ProxyFactory.prototype._add_method = function(proxy, method_name){
    var method = function () {
        var args, result;
        // In here, 'this' refers to the proxy!
        //
        // In JS, 'arguments' is not a real array, so this converts it to one!
        args   = Array.prototype.slice.call(arguments);
        result = this.__broker__.invoke_request(
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
    var get, set;

    get = function() {
        // In here, 'this' refers to the proxy!
        return this.__broker__.invoke_request('get_trait', [this, trait_name]);
    };

    set = function(value) {
        // In here, 'this' refers to the proxy!
        this.__broker__.invoke_request('set_trait', [this, trait_name, value]);
    };

    this._add_property(proxy, trait_name, get, set);
};

jigna.ProxyFactory.prototype._create_instance_proxy = function(id) {
    var index, info, method_names, proxy, trait_names;

    proxy = new jigna.Proxy(id, this._broker);
    info  = this._broker.invoke_request('get_instance_info', [proxy]);

    trait_names = info.trait_names;
    for (index in trait_names) {
        this._add_trait_property(proxy, trait_names[index]);
    }

    method_names = info.method_names;
    for (index in method_names) {
        this._add_method(proxy, method_names[index]);
    }

    return proxy;
};

jigna.ProxyFactory.prototype._create_list_proxy = function(id) {
    var index, info, proxy;

    proxy = new jigna.Proxy(id, this._broker);
    info  = this._broker.invoke_request('get_list_info', [proxy]);

    for (index=0; index < info.length; index++) {
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
