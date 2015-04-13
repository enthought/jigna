///////////////////////////////////////////////////////////////////////////////
// ProxyFactory
///////////////////////////////////////////////////////////////////////////////

jigna.ProxyFactory = function(client) {
    // Private protocol.
    this._client = client;
};

jigna.ProxyFactory.prototype.create_proxy = function(type, obj, info) {
    /* Create a proxy for the given type and value. */

    var factory_method = this['_create_' + type + '_proxy'];
    if (factory_method === undefined) {
	throw 'cannot create proxy for: ' + type;
    }

    // Create a cache object corresponding to this proxy
    if (this._client._id_to_cache_map[obj] === undefined) {
	this._client._id_to_cache_map[obj] = {};
    }
    return factory_method.apply(this, [obj, info]);
};

// Private protocol //////////////////////////////////////////////////////////

jigna.ProxyFactory.prototype._add_item_attribute = function(proxy, index){
    var descriptor, get, set;

    get = function() {
	// In here, 'this' refers to the proxy!
	var cache = this.__client__._id_to_cache_map[this.__id__];
	var value = cache[index];
	if (value === undefined) {
	    value = this.__client__.get_attribute(this, index);
		cache[index] = value;
	}

	return value;
    };

    set = function(value) {
	// In here, 'this' refers to the proxy!
	var cache = this.__client__._id_to_cache_map[this.__id__];
	cache[index] = value;
	this.__client__.set_item(this.__id__, index, value);
    };

    descriptor = {enumerable:true, get:get, set:set, configurable:true};
    Object.defineProperty(proxy, index, descriptor);
};

jigna.ProxyFactory.prototype._add_instance_method = function(proxy, method_name){
    proxy[method_name] = function() {
	// In here, 'this' refers to the proxy!
	var args = Array.prototype.slice.call(arguments);
	return this.__client__.call_instance_method(
	    this.__id__, method_name, args
	);
    };
};

jigna.ProxyFactory.prototype._add_instance_attribute = function(proxy, attribute_name){
    var descriptor, get, set;

    get = function() {
	// In here, 'this' refers to the proxy!
	var cache = this.__client__._id_to_cache_map[this.__id__];
	var value = cache[attribute_name];
	if (value === undefined) {
	    value = this.__client__.get_attribute(this, attribute_name);
		cache[attribute_name] = value;
	}

	return value;
    };

    set = function(value) {
	// In here, 'this' refers to the proxy!
	//
	// If the proxy is for a 'HasTraits' instance then we don't need
	// to set the cached value here as the value will get updated when
	// we get the corresponding trait event. However, setting the value
	// here means that we can create jigna UIs for non-traits objects - it
	// just means we won't react to external changes to the model(s).
	var cache = this.__client__._id_to_cache_map[this.__id__];
	cache[attribute_name] = value;
	this.__client__.set_instance_attribute(
	    this.__id__, attribute_name, value
	);
    };

    descriptor = {enumerable:true, get:get, set:set, configurable:true};
    Object.defineProperty(proxy, attribute_name, descriptor);
};

jigna.ProxyFactory.prototype._add_instance_event = function(proxy, event_name){
    var descriptor, set;

    set = function(value) {
	var cache = this.__client__._id_to_cache_map[this.__id__];
	cache[event_name] = value;
	this.__client__.set_instance_attribute(
	    this.__id__, event_name, value
	);
    };

    descriptor = {enumerable:false, set:set, configurable: true};
    Object.defineProperty(proxy, event_name, descriptor);
};

jigna.ProxyFactory.prototype._create_dict_proxy = function(id, info) {
    var index, proxy;

    // fixme: smell - the proxy factory shouldn't be determining whether it
    // needs to create a proxy or not (the giveaway is that to make the decision
    // it looks at state of the client!)...
    proxy = this._client._id_to_proxy_map[id];
    if (proxy === undefined) {
	proxy = new jigna.Proxy('dict', id, this._client);

    } else {
	this._delete_dict_keys(proxy);
    }

    for (index in info.keys) {
	this._add_item_attribute(proxy, info.keys[index]);
    }
    return proxy;
};

jigna.ProxyFactory.prototype._create_instance_proxy = function(id, info) {
    var constructor, index, proxy;

    // We create a constructor for each Python class and then create the
    // actual proxies as from those.
    constructor = this._client._type_to_constructor_map[info.type_name];
    if (constructor === undefined) {
	constructor = this._create_constructor(info);
	this._client._type_to_constructor_map[info.type_name] = constructor;
    }

    proxy = this._client._id_to_proxy_map[id];
    if (proxy === undefined) {
	this._client.print_JS_message('Creating new instance proxy');
	this._client.print_JS_message('Id: ' + id + ' Type: ' + info.type_name);
	proxy = new constructor('instance', id, this._client);

	for (index in info.attribute_names) {
	    jigna.add_listener(
		proxy,
		info.attribute_names[index],
		this._client.on_object_changed,
		this._client
	    );
	}

	for (index in info.event_names) {
	    jigna.add_listener(
		proxy,
		info.event_names[index],
		this._client.on_object_changed,
		this._client
	    );
	}

    } else {
	this._client.print_JS_message('Reusing instance proxy');
	this._client.print_JS_message('Id: ' + id + ' Type: ' + info.type_name);
    }

    return proxy;
};

jigna.ProxyFactory.prototype._create_list_proxy = function(id, info) {
    var index, proxy;

    // fixme: smell - the proxy factory shouldn't be determining whether it
    // needs to create a proxy or not (the giveaway is that to make the decision
    // it looks at state of the client!)...
    proxy = this._client._id_to_proxy_map[id];
    if (proxy === undefined) {
	proxy = new jigna.ListProxy('list', id, this._client);

    } else {
	this._delete_list_items(proxy);
    }

    for (index=0; index < info.length; index++) {
	this._add_item_attribute(proxy, index);
    }

    return proxy;
};

jigna.ProxyFactory.prototype._create_constructor = function(info) {
    this._client.print_JS_message('creating constructor: ' + info.type_name);

    constructor = function(type, id, client) {
	jigna.Proxy.call(this, type, id, client);
    };

    constructor.prototype = Object.create(jigna.Proxy.prototype);
    constructor.prototype.constructor = constructor;

    for (index in info.attribute_names) {
	this._add_instance_attribute(
	    constructor.prototype, info.attribute_names[index]
	);
    }

    for (index in info.event_names) {
	this._add_instance_event(
	    constructor.prototype, info.event_names[index]
	);
    }

    for (index in info.method_names) {
	this._add_instance_method(
	    constructor.prototype, info.method_names[index]
	);
    }

    // This property is not actually used by jigna itself. It is only there to
    // make it easy to see what the type of the server-side object is when
    // debugging the JS code in the web inspector.
    Object.defineProperty(
	constructor.prototype, '__type_name__', {value : info.type_name}
    );

    return constructor;
}

jigna.ProxyFactory.prototype._delete_dict_keys = function(proxy) {
    /* Delete all keys of a previously used dict proxy. */
    var index, keys;

    keys = Object.keys(proxy);
    for (index in keys) {
	delete proxy[keys[index]];
    }
};

jigna.ProxyFactory.prototype._delete_list_items = function(proxy) {
    /* Delete all items of a previously used list proxy. */
    var index;

    for (index=0; index < proxy.length; index++) {
	delete proxy[index];
    }
};
