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

// fixme: factory function for jigna.Client?
jigna.initialize = function(model_name, id) {
    jigna.broker = new jigna.Broker();
    jigna.broker.initialize(model_name, id);
};

///////////////////////////////////////////////////////////////////////////////
// Bridge
///////////////////////////////////////////////////////////////////////////////

// fixme: jigna.Client
jigna.Bridge = function() {
    // Private protocol
    this._python = window['python'];
};

jigna.Bridge.prototype.send_request = function(method_name, args) {
    var request = {
        'method_name' : method_name,
        'args'        : args
    };

    var response = JSON.parse(
        this._python.handle_request(JSON.stringify(request))
    );
    if (response.exception !== null) {
        throw response.value;
    }

    return response;
};

///////////////////////////////////////////////////////////////////////////////
// Broker
///////////////////////////////////////////////////////////////////////////////

jigna.Broker = function() {
    // Private protocol
    this._bridge          = new jigna.Bridge();
    this._id_to_proxy_map = {};
    this._proxy_factory   = new jigna.ProxyFactory(this);
    this._scope           = $(document.body).scope();
};

jigna.Broker.prototype.initialize = function(model_name, id) {
    // Get a proxy for the object identified by Id...
    var proxy = this._create_proxy('instance', id);

    // ... and expose it with the name 'model_name' to AngularJS.
    var scope = this._scope;
    scope.$apply(function() {scope[model_name] = proxy;});
};

// fixme: This smells like part of bridge as it is called directly from
// Python and has JSON-malarky in it!
jigna.Broker.prototype.on_object_changed = function(event_json) {

    var event = JSON.parse(event_json);

    this._create_proxy(event.type, event.value);

    if (this._scope.$$phase === null){
        this._scope.$digest();
    }
};

// Instances...
jigna.Broker.prototype.call_method = function(id, method_name, args) {
    // fixme: Why is this method different to the others... Could we put
    // this id wrangling in 'send_request'?
    var args = Array.prototype.slice.call(args);
    for (var index in args) {
        var value = args[index];
        if (value.__id__ !== undefined) {
            args[index] = {'__id__' : value.__id__};
        }
    };

    return this._send_request('call_method', [id, method_name].concat(args));
};

jigna.Broker.prototype.get_instance_info = function(id) {
    return this._send_request('get_instance_info', [id]);
};

jigna.Broker.prototype.get_trait = function(id, trait_name) {
    return this._send_request('get_trait', [id, trait_name]);
};

jigna.Broker.prototype.set_trait = function(id, trait_name, value) {
    return this._send_request('set_trait', [id, trait_name, value]);
};

// Lists...
jigna.Broker.prototype.get_list_info = function(id) {
    return this._send_request('get_list_info', [id]);
};

jigna.Broker.prototype.get_list_item = function(id, index) {
    return this._send_request('get_list_item', [id, index]);
};

jigna.Broker.prototype.set_list_item = function(id, index, value){
    return this._send_request('set_list_item', [id, index, value]);
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

jigna.Broker.prototype._get_proxy = function(type, obj) {
    var proxy;

    if (type === 'primitive') {
        proxy = obj;
    }
    else {
        proxy = this._id_to_proxy_map[obj];
        if (proxy === undefined) {
            proxy = this._create_proxy(type, obj);
        }
    }

    return proxy;
};

jigna.Broker.prototype._send_request = function(method_name, args) {
    var response = this._bridge.send_request(method_name, args);

    return this._get_proxy(response.type, response.value);
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
    var get = function() {
        // In here, 'this' refers to the proxy!
        return this.__broker__.get_list_item(this.__id__, index);
    };

    var set = function(value) {
        // In here, 'this' refers to the proxy!
        this.__broker__.set_list_item(this.__id__, index, value);
    };

    this._add_property(proxy, index, get, set);
};

jigna.ProxyFactory.prototype._add_method = function(proxy, method_name){
    var method = function () {
        // In here, 'this' refers to the proxy!
        return this.__broker__.call_method(this.__id__, method_name, arguments);
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
        return this.__broker__.get_trait(this.__id__, trait_name);
    };

    var set = function(value) {
        // In here, 'this' refers to the proxy!
        this.__broker__.set_trait(this.__id__, trait_name, value);
    };

    this._add_property(proxy, trait_name, get, set);
};

jigna.ProxyFactory.prototype._create_instance_proxy = function(id) {
    var proxy = new jigna.Proxy(id, this._broker);
    var info = this._broker.get_instance_info(id);

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
    var list_length = this._broker.get_list_info(id);

    for (var index=0; index < list_length; index++) {
        this._add_list_item_property(proxy, index);
    }

    return proxy;
};

///////////////////////////////////////////////////////////////////////////////
// Proxy
///////////////////////////////////////////////////////////////////////////////

jigna.Proxy = function(id, broker) {
    var descriptor = {
        configurable : true,
        enumerable   : false,
        writeable    : true
    };

    descriptor.value = id;
    Object.defineProperty(this, '__id__', descriptor);

    descriptor.value = broker;
    Object.defineProperty(this, '__broker__', descriptor);
};

// EOF ////////////////////////////////////////////////////////////////////////
