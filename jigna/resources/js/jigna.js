//
// Enthought product code
//
// (C) Copyright 2013 Enthought, Inc., Austin, TX
// All right reserved.
//
// This file is confidential and NOT open source.  Do not distribute.
//

var jigna = {};

///////////////////////////////////////////////////////////////////////////////
// Bridge
///////////////////////////////////////////////////////////////////////////////

jigna.Bridge = function(scope) {
    // Bridge protocol.
    this.scope = scope;

    // Private protocol
    this._bridge          = window['python_bridge'];
    this._id_to_proxy_map = {};
    this._proxy_factory   = new jigna.ProxyFactory(this);
};

jigna.Bridge.prototype.initialize = function(model_name, id) {
    // Get a proxy for the object identified by Id...
    var proxy = this._create_proxy('instance', id);

    // ... and expose it with the name 'model_name' to AngularJS.
    this.scope.$apply(
        function() {jigna.bridge.scope[model_name] = proxy;}
    );
};

jigna.Bridge.prototype.get = function(request) {
    var result = JSON.parse(this._bridge.get(JSON.stringify(request)));
    if (result.exception !== null) {
        throw result.exception;
    }

    return result;
};

jigna.Bridge.prototype.on_object_changed = function(type, value) {
    this._create_proxy(type, value);

    if (this.scope.$$phase === null){
        this.scope.$digest();
    }
};

// Instances...
jigna.Bridge.prototype.call_method = function(id, method_name) {
    var request = {
        'method_name' : 'call_method',
        'args'        : [id, method_name]
    };

    var response = this.get(request);

    return response.value;
};

jigna.Bridge.prototype.get_instance_info = function(id) {
    var request = {
        'method_name' : 'get_instance_info',
        'args'        : [id]
    };

    var response = this.get(request);

    return response.value;
};

jigna.Bridge.prototype.get_trait = function(id, trait_name) {
    var request = {
        'method_name' : 'get_trait',
        'args'        : [id, trait_name]
    };

    var response = this.get(request);

    return this._get_proxy(response.type, response.value);
};

jigna.Bridge.prototype.set_trait = function(id, trait_name, value) {
    var request = {
        'method_name' : 'set_trait',
        'args'        : [id, trait_name, value]
    };

    this.get(request);
};

// Lists...
jigna.Bridge.prototype.get_list_info = function(id) {
    var request = {
        'method_name' : 'get_list_info',
        'args'        : [id]
    };

    var response = this.get(request);

    return response.value;
};

jigna.Bridge.prototype.get_list_item = function(id, index) {
    var request = {
        'method_name' : 'get_list_item',
        'args'        : [id, index],
    };

    var response = this.get(request);

    return this._get_proxy(response.type, response.value);
};

jigna.Bridge.prototype.set_list_item = function(id, index, value){
    var request = {
        'method_name' : 'set_list_item',
        'args'        : [id, index, value],
    };

    this.get(request);
};

// Private protocol //////////////////////////////////////////////////////////

jigna.Bridge.prototype._create_proxy = function(type, obj) {
    var proxy = this._proxy_factory.create_proxy(type, obj);
    this._id_to_proxy_map[obj] = proxy;

    return proxy;
};

jigna.Bridge.prototype._get_proxy = function(type, obj) {
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

///////////////////////////////////////////////////////////////////////////////
// ProxyFactory
///////////////////////////////////////////////////////////////////////////////

jigna.ProxyFactory = function(bridge) {
    // Private protocol.
    this._bridge = bridge;
};

jigna.ProxyFactory.prototype.create_proxy = function(type, obj) {
    /* Make a proxy for the given value (typed by type!). */

    var proxy;

    if (type === 'primitive') {
        proxy = obj;
    }
    else {
        if (type === 'instance') {
            proxy = this._create_instance_proxy(obj);
        }
        else if (type === 'list') {
            proxy = this._create_list_proxy(obj);
        }
        else {
            throw 'cannot create proxy for type: ' + type;
        }
    }

    return proxy;
};

// Private protocol //////////////////////////////////////////////////////////

jigna.ProxyFactory.prototype._add_list_item_property = function(proxy, index){
    var get = function() {
        // In here, 'this' refers to the proxy!
        return this._bridge.get_list_item(this._id, index);
    };

    var set = function(value) {
        // In here, 'this' refers to the proxy!
        this._bridge.set_list_item(this._id, index, value);
    };

    this._add_property(proxy, index, get, set);
};

jigna.ProxyFactory.prototype._add_method = function(proxy, method_name){
    var method = function () {
        // In here, 'this' refers to the proxy!
        return this._bridge.call_method(this._id, method_name);
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
        return this._bridge.get_trait(this._id, trait_name);
    };

    var set = function(value) {
        // In here, 'this' refers to the proxy!
        this._bridge.set_trait(this._id, trait_name, value);
    };

    this._add_property(proxy, trait_name, get, set);
};

jigna.ProxyFactory.prototype._create_instance_proxy = function(id) {
    var proxy = new jigna.Proxy(id, this._bridge);
    var info = this._bridge.get_instance_info(id);

    var trait_names = info['trait_names']
    for (var index in trait_names) {
        this._add_trait_property(proxy, trait_names[index]);
    }

    var method_names = info['method_names']
    for (var index in method_names) {
        this._add_method(proxy, method_names[index]);
    }

    return proxy;
};

jigna.ProxyFactory.prototype._create_list_proxy = function(id) {
    var proxy = new jigna.Proxy(id, this._bridge);
    var list_length = this._bridge.get_list_info(id);
    for (var index=0; index < list_length; index++) {
        this._add_list_item_property(proxy, index);
    }

    return proxy;
};

///////////////////////////////////////////////////////////////////////////////
// Proxy
///////////////////////////////////////////////////////////////////////////////

jigna.Proxy = function(id, bridge) {
    var descriptor = {
        configurable : true,
        enumerable   : false,
        writeable    : true
    };

    descriptor.value = id;
    Object.defineProperty(this, '_id', descriptor);

    descriptor.value = bridge;
    Object.defineProperty(this, '_bridge', descriptor);
};

///////////////////////////////////////////////////////////////////////////////

$(document).ready(
    function() {
        var scope = $(document.body).scope();
        jigna.bridge = new jigna.Bridge(scope);
    }
);

// EOF ////////////////////////////////////////////////////////////////////////
