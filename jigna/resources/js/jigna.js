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
// AngularJS
///////////////////////////////////////////////////////////////////////////////

// Put everything specific to AngularJS in here.
jigna.AngularJS = function() {
    // AngularJS protocol.
    this.scope  = $(document.body).scope();
};

jigna.AngularJS.prototype.add_model = function(model_name, model) {
    var scope;

    scope = this.scope;
    scope.$apply(function() {scope[model_name] = model;});
};

jigna.AngularJS.prototype.on_object_changed = function(event) {
    if (this.scope.$$phase === null){
        this.scope.$digest();
    }
};

///////////////////////////////////////////////////////////////////////////////
// Client
///////////////////////////////////////////////////////////////////////////////

jigna.Client = function() {
    var request, response;

    // Private protocol
    this._id_to_proxy_map = {};
    this._proxy_factory   = new jigna.ProxyFactory(this);

    // Client protocol.
    this.bridge       = this._create_bridge();
    this.js_framework = new jigna.AngularJS();

    request  = {kind : 'get_context'};
    response = this.send_request(request);

    this.models       = this._add_models(response.result);
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

jigna.Client.prototype.send_request = function(request) {
    /* Send a request to the server and wait for (and return) the response. */

    var jsonized_request, jsonized_response, response;

    jsonized_request  = JSON.stringify(request);
    jsonized_response = this.bridge.send_request(jsonized_request);
    response          = JSON.parse(jsonized_response);

    if (response.exception !== null) throw response.exception;

    return response;
};

// Convenience methods for each kind of request //////////////////////////////

// ... ?

// Private protocol //////////////////////////////////////////////////////////

jigna.Client.prototype._add_model = function(model_name, id) {
    var proxy;

    // Create a proxy for the object identified by the Id...
    proxy = this._create_proxy('instance', id);

    // ... and expose it with the name 'model_name' to the JS framework.
    this.js_framework.add_model(model_name, proxy);

    return proxy;
};

jigna.Client.prototype._add_models = function(context) {
    var models, model_name;

    models = {};
    for (model_name in context) {
        models[model_name] = this._add_model(model_name, context[model_name]);
    }

    return models;
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

jigna.Client.prototype._invalidate_cached_attribute = function(id, attribute_name) {
    var proxy = this._id_to_proxy_map[id];
    proxy.__cache__[attribute_name] = undefined;
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
    this._invalidate_cached_attribute(event.obj, event.attribute_name);

    // fixme: This smells... It is used when we have a list of instances but it
    // blows away caching advantages. Can we make it smarter by managing the
    // details of a TraitListEvent?
    this._create_proxy(event.new_obj.type, event.new_obj.value);

    // Let the JS-framework know about the change.
    this.js_framework.on_object_changed(event);
};

///////////////////////////////////////////////////////////////////////////////
// ProxyFactory
///////////////////////////////////////////////////////////////////////////////

jigna.ProxyFactory = function(client) {
    // Private protocol.
    this._client = client;
};

jigna.ProxyFactory.prototype.create_proxy = function(type, obj) {
    /* Make a proxy for the given type and value. */

    var factory_method = this['_create_' + type + '_proxy'];
    if (factory_method === undefined) {
        throw 'cannot create proxy for: ' + type;
    }

    return factory_method.apply(this, [obj]);
};

// Private protocol //////////////////////////////////////////////////////////

jigna.ProxyFactory.prototype._add_item_attribute = function(proxy, index){
    var descriptor, get, set;

    get = function() {
        // In here, 'this' refers to the proxy!
        var request, response;

        request = {
            kind  : 'get_item',
            id    : this.__id__,
            index : index,
        };

        response = this.__client__.send_request(request)

        return this.__client__._unmarshal(response.result);
    };

    set = function(value) {
        // In here, 'this' refers to the proxy!
        var request;

        request = {
            kind  : 'set_item',
            id    : this.__id__,
            index : index,
            value : this.__client__._marshal(value)
        };

        this.__client__.send_request(request)
    };

    descriptor = {enumerable:true, get:get, set:set};
    Object.defineProperty(proxy, index, descriptor);
};

jigna.ProxyFactory.prototype._add_instance_method = function(proxy, method_name){
    var method = function () {
        var args, request, response;

        args     = Array.prototype.slice.call(arguments);
        request  = {
            kind        : 'call_instance_method',
            id          : this.__id__,
            method_name : method_name,
            args        : this.__client__._marshal_all(args)
        };
        response = this.__client__.send_request(request)

        return this.__client__._unmarshal(response.result)
    };

    proxy[method_name] = method;
};

jigna.ProxyFactory.prototype._add_instance_attribute = function(proxy, attribute_name){
    var descriptor, get, set;

    get = function() {
        // In here, 'this' refers to the proxy!
        var cached_value, request, response, value;

        cached_value = this.__cache__[attribute_name];
        if (cached_value !== undefined) {
            value = cached_value;

        } else {
            request = {
                kind           : 'get_instance_attribute',
                id             : this.__id__,
                attribute_name : attribute_name
            };

            response = this.__client__.send_request(request)
            value    = this.__client__._unmarshal(response.result);

            this.__cache__[attribute_name] = value;
        }

        return value;
    };

    set = function(value) {
        // If the proxy is for a 'HasTraits' instance then we don't need
        // to set the cached value here as the value will get updated when
        // we get the corresponsing trait event. However, setting the value
        // here means that we can create jigna UIs for non-traits objects - it
        // just means we won't react to external changes to the model(s).
        this.__cache__[attribute_name] = value;

        request = {
            kind           : 'set_instance_attribute',
            id             : this.__id__,
            attribute_name : attribute_name,
            value          : this.__client__._marshal(value)
        };

        this.__client__.send_request(request)
    };

    descriptor = {enumerable:true, get:get, set:set};
    Object.defineProperty(proxy, attribute_name, descriptor);
};

jigna.ProxyFactory.prototype._create_dict_proxy = function(id) {
    var index, info, proxy, request, response;

    proxy = new jigna.Proxy(id, this._client);
    Object.defineProperty(proxy, '__type__', {value:'dict'});

    request  = {kind : 'get_dict_info', id : proxy.__id__};
    response = this._client.send_request(request);
    info     = response.result;

    for (index in info.keys) {
        this._add_item_attribute(proxy, info.keys[index]);
    }

    return proxy;
};

jigna.ProxyFactory.prototype._create_instance_proxy = function(id) {
    var index, info, proxy, request, response;

    proxy = new jigna.Proxy(id, this._client);
    Object.defineProperty(proxy, '__type__', {value:'instance'});

    request  = {kind : 'get_instance_info', id : proxy.__id__};
    response = this._client.send_request(request);
    info     = response.result;

    for (index in info.attribute_names) {
        this._add_instance_attribute(proxy, info.attribute_names[index]);
    }

    for (index in info.method_names) {
        this._add_instance_method(proxy, info.method_names[index]);
    }

    // This property is not actually used by jigna at all! It is only there to
    // make it easy to see what the type of the server-side object is when
    // debugging the JS code.
    Object.defineProperty(proxy, '__type_name__', {value : info.type_name});

    return proxy;
};

jigna.ProxyFactory.prototype._create_list_proxy = function(id) {
    var index, info, proxy, request, response;

    proxy = new jigna.Proxy(id, this._client);
    Object.defineProperty(proxy, '__type__', {value : 'list'});

    request  = {kind : 'get_list_info', id : proxy.__id__};
    response = this._client.send_request(request);
    info     = response.result;

    for (index=0; index < info.length; index++) {
        this._add_item_attribute(proxy, index);
    }

    return proxy;
};

///////////////////////////////////////////////////////////////////////////////
// Proxy
///////////////////////////////////////////////////////////////////////////////

jigna.Proxy = function(id, client) {
    Object.defineProperty(this, '__id__',     {value : id});
    Object.defineProperty(this, '__client__', {value : client});
    Object.defineProperty(this, '__cache__',  {value : {}});
};

///////////////////////////////////////////////////////////////////////////////
// Auto-initialization!
///////////////////////////////////////////////////////////////////////////////

$(document).ready(function(){
    jigna.initialize();
});

// EOF ////////////////////////////////////////////////////////////////////////
