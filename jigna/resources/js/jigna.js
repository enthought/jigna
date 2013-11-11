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

jigna.initialize = function() {
    this.client = new jigna.Client();
};

///////////////////////////////////////////////////////////////////////////////
// QtBridge (intra-process)
///////////////////////////////////////////////////////////////////////////////

jigna.QtBridge = function(client, qt_bridge) {
    // Private protocol
    this._client    = client;
    this._qt_bridge = qt_bridge;
};

jigna.QtBridge.prototype.handle_event = function(jsonized_event) {
    /* Handle an event from the server. */
    this._client.handle_event(jsonized_event);
};

jigna.QtBridge.prototype.send_request = function(jsonized_request) {
    /* Send a request to the server and wait for the reply. */

    return this._qt_bridge.handle_request(jsonized_request);
};

///////////////////////////////////////////////////////////////////////////////
// WebBridge
///////////////////////////////////////////////////////////////////////////////

jigna.WebBridge = function(client) {
    var url = 'ws://' + window.location.host + '/_jigna_ws';

    this._web_socket = new WebSocket(url);
    this._web_socket.onmessage = function(event) {
        client.handle_event(event.data);
    };
};

jigna.WebBridge.prototype.send_request = function(jsonized_request) {
    /* Send a request to the server and wait for the reply. */

    var jsonized_response;

    $.ajax(
        {
            url     : '/_jigna',
            type    : 'GET',
            data    : {'data': jsonized_request},
            success : function(result) {jsonized_response = result;},
            async   : false
        }
    );

    return jsonized_response;
};

///////////////////////////////////////////////////////////////////////////////
// Client
///////////////////////////////////////////////////////////////////////////////

jigna.Client = function() {
    // Client protocol.
    this.bridge = this._create_bridge();
    this.scope  = $(document.body).scope();

    // Private protocol
    this._id_to_proxy_map = {};
    this._proxy_factory   = new jigna.ProxyFactory(this);

    // Add the models in the server's context.
    this._add_models(this.send_request('get_context', []));
};

jigna.Client.prototype.handle_event = function(jsonized_event) {
    /* Handle an event from the server. */
    var event = JSON.parse(jsonized_event);

    // Currently, the only event we handle is 'on_object_changed'!
    var handler = this['_on_' + event.kind];
    if (handler === undefined) {
        throw 'no handler for event: ' + event.kind
    }

    handler.apply(this, [event]);
};

jigna.Client.prototype.send_request = function(kind, args) {
    /* Send a request to the server and wait for the reply. */

    var jsonized_request, jsonized_response, request, response, result;

    request           = {'kind' : kind, 'args' : this._marshal_all(args)};
    jsonized_request  = JSON.stringify(request);
    jsonized_response = this.bridge.send_request(jsonized_request);
    response          = JSON.parse(jsonized_response);
    result            = this._unmarshal(response.result);

    if (response.exception !== null) {
        throw result;
    }

    return result;
};

// Private protocol //////////////////////////////////////////////////////////

jigna.Client.prototype._add_model = function(model_name, id) {
    var proxy, scope;

    // Create a proxy for the object identified by the Id...
    proxy = this._create_proxy('instance', id);

    // ... and expose it with the name 'model_name' to AngularJS.
    scope = this.scope;
    scope.$apply(function() {scope[model_name] = proxy;});
};

jigna.Client.prototype._add_models = function(context) {
    var model_name;

    for (model_name in context) {
        this._add_model(model_name, context[model_name]);
    }
}

jigna.Client.prototype._create_bridge = function() {
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

jigna.Client.prototype._create_proxy = function(type, obj) {
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

jigna.Client.prototype._invalidate_cached_value = function(id, attribute_name) {
    var proxy = this._id_to_proxy_map[id];
    proxy.__cache__[attribute_name] = undefined;
};

jigna.Client.prototype._marshal = function(obj) {
    var type, value;

    // If the object is null, undefined or anything *other* than a proxy!
    if (obj === null || obj === undefined || obj.__id__ === undefined) {
        type  = 'primitive';
        value = obj;

    // Otherwise, the object is a proxy!
    } else {
        type  = obj.__type__;
        value = obj.__id__;
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

jigna.Client.prototype._unmarshal_all = function(objs) {
    var index;

    for (index in objs) {
        objs[index] = this._unmarshal(objs[index]);
    }

    // For convenience, as we modify the array in-place.
    return objs;
};

jigna.Client.prototype._on_object_changed = function(event) {
    // Invalidate any cached value on the proxy.
    this._invalidate_cached_value(event.obj, event.attribute_name);

    // fixme: This smells... It is used to recreate a list proxy every time
    // a list changes but that blows away caching advantages. Can we make it
    // smarter by managing the details of a TraitListEvent?
    this._create_proxy(event.new_obj.type, event.new_obj.value);

    if (this.scope.$$phase === null){
        this.scope.$digest();
    }
};

///////////////////////////////////////////////////////////////////////////////
// ProxyFactory
///////////////////////////////////////////////////////////////////////////////

jigna.ProxyFactory = function(client) {
    // Private protocol.
    this._client = client;
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

jigna.ProxyFactory.prototype._add_list_item_attribute = function(proxy, index){
    var get, set;

    get = function() {
        // In here, 'this' refers to the proxy!
        return this.__client__.send_request('get_list_item', [this, index]);
    };

    set = function(value) {
        // In here, 'this' refers to the proxy!
        this.__client__.send_request('set_list_item', [this, index, value]);
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
        result = this.__client__.send_request(
            'call_instance_method', [this, method_name].concat(args)
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

jigna.ProxyFactory.prototype._add_attribute = function(proxy, attribute_name){
    var get, set;

    get = function() {
        // In here, 'this' refers to the proxy!
        var cached_value, value;

        cached_value = this.__cache__[attribute_name];
        if (cached_value !== undefined) {
            value = cached_value;

        } else {
            value = this.__client__.send_request(
                'get_instance_attribute', [this, attribute_name]
            );
            this.__cache__[attribute_name] = value;
        }

        return value;
    };

    set = function(value) {
        this.__client__.send_request(
            'set_instance_attribute', [this, attribute_name, value]
        );
    };

    this._add_property(proxy, attribute_name, get, set);
};

jigna.ProxyFactory.prototype._create_instance_proxy = function(id) {
    var attribute_names, index, info, method_names, proxy;

    proxy = new jigna.Proxy(id, this._client);

    var descriptor = {
        configurable : true,
        enumerable   : false,
        writeable    : false,
        value        : 'instance'
    };
    Object.defineProperty(proxy, '__type__', descriptor);

    info = this._client.send_request('get_instance_info', [proxy]);

    attribute_names = info.attribute_names;
    for (index in attribute_names) {
        this._add_attribute(proxy, attribute_names[index]);
    }

    method_names = info.method_names;
    for (index in method_names) {
        this._add_method(proxy, method_names[index]);
    }

    // This property is not actually used by jigna at all! It is only there to
    // make it easy to see what the type of the server-side object is when
    // debugging the JS code.
    descriptor.value = info.type_name;
    Object.defineProperty(proxy, '__type_name__', descriptor);

    return proxy;
};

jigna.ProxyFactory.prototype._create_list_proxy = function(id) {
    var index, info, proxy;

    proxy = new jigna.Proxy(id, this._client);

    var descriptor = {
        configurable : true,
        enumerable   : false,
        writeable    : false,
        value        : 'list'
    };
    Object.defineProperty(proxy, '__type__', descriptor);

    info  = this._client.send_request('get_list_info', [proxy]);

    for (index=0; index < info.length; index++) {
        this._add_list_item_attribute(proxy, index);
    }

    return proxy;
};

///////////////////////////////////////////////////////////////////////////////
// Proxy
///////////////////////////////////////////////////////////////////////////////

jigna.Proxy = function(id, client) {
    var descriptor = {configurable:true, enumerable:false, writeable:true};

    descriptor.value = id;
    Object.defineProperty(this, '__id__', descriptor);

    descriptor.value = client;
    Object.defineProperty(this, '__client__', descriptor);

    descriptor.value = {};
    Object.defineProperty(this, '__cache__', descriptor);
};

///////////////////////////////////////////////////////////////////////////////
// Auto-initialization!
///////////////////////////////////////////////////////////////////////////////

$(document).ready(function(){
    jigna.initialize();
});

// EOF ////////////////////////////////////////////////////////////////////////
