///////////////////////////////////////////////////////////////////////////////
// ProxyFactory
///////////////////////////////////////////////////////////////////////////////

jigna.ProxyFactory = function(client) {
    // Private protocol.
    this._client = client;

    // We create a constructor for each Python class and then create the
    // actual proxies from those.
    this._type_to_constructor_map = {};

    // Create a new instance constructor when a "new_type" event is fired.
    jigna.add_listener(
        'jigna',
        'new_type',
        function(event){this._create_instance_constructor(event.data);},
        this
    );

};

jigna.ProxyFactory.prototype.create_proxy = function(type, id, info) {
    /* Create a proxy for the given type, id and value. */

    var factory_method = this['_create_' + type + '_proxy'];
    if (factory_method === undefined) {
        throw 'cannot create proxy for: ' + type;
    }

    return factory_method.apply(this, [id, info]);
};

jigna.ProxyFactory.prototype.update_proxy = function(proxy, type, info) {
    /* Update the given proxy.
     *
     * This is only used for list and dict proxies when their items have
     * changed.
     */

    var factory_method = this['_update_' + type + '_proxy'];
    if (factory_method === undefined) {
        throw 'cannot update proxy for: ' + type;
    }

    return factory_method.apply(this, [proxy, info]);
};

// Private protocol ////////////////////////////////////////////////////////////

// Instance proxy creation /////////////////////////////////////////////////////

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
        var value = this.__cache__[attribute_name];
        if (value === undefined) {
            value = this.__client__.get_attribute(this, attribute_name);
            this.__cache__[attribute_name] = value;
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
        this.__cache__[attribute_name] = value;
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
        this.__cache__[event_name] = value;
        this.__client__.set_instance_attribute(
            this.__id__, event_name, value
        );
    };

    descriptor = {enumerable:false, set:set, configurable: true};
    Object.defineProperty(proxy, event_name, descriptor);
};

jigna.ProxyFactory.prototype._create_instance_constructor = function(info) {
    var constructor = this._type_to_constructor_map[info.type_name];
    if (constructor !== undefined) {
        return constructor;
    }

    constructor = function(type, id, client) {
        jigna.Proxy.call(this, type, id, client);

        /* Listen for changes to the object that the proxy is a proxy for! */
        var index;
        var info = this.__info__;

        for (index in info.attribute_names) {
            jigna.add_listener(
                this,
                info.attribute_names[index],
                client.on_object_changed,
                client
            );
        }

        for (index in info.event_names) {
            jigna.add_listener(
                this,
                info.event_names[index],
                client.on_object_changed,
                client
            );
        }
    };

    // This is the standard way to set up protoype inheritance in JS.
    //
    // The line below says "when the function 'constructor' is called via the
    // 'new' operator, then set the prototype of the created object to the
    // given object".
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

    // The info is only sent to us once per type, and so we store it in the
    // prototype so that we can use it in the constructor to get the names
    // of any atttributes and events.
    Object.defineProperty(
        constructor.prototype, '__info__', {value : info}
    );

    // This property is not actually used by jigna itself. It is only there to
    // make it easy to see what the type of the server-side object is when
    // debugging the JS code in the web inspector.
    Object.defineProperty(
        constructor.prototype, '__type_name__', {value : info.type_name}
    );

    this._type_to_constructor_map[info.type_name] = constructor;

    return constructor;
}

jigna.ProxyFactory.prototype._create_instance_proxy = function(id, info) {
    var constructor, proxy;

    // We create a constructor for each Python class and then create the
    // actual proxies as from those.
    constructor = this._type_to_constructor_map[info.type_name];
    if (constructor === undefined) {
        constructor = this._create_instance_constructor(info);
    }

    return new constructor('instance', id, this._client);
};

// Dict proxy creation /////////////////////////////////////////////////////////

jigna.ProxyFactory.prototype._create_dict_proxy = function(id, info) {
    var proxy = new jigna.Proxy('dict', id, this._client);
    this._populate_dict_proxy(proxy, info);

    return proxy;
};

jigna.ProxyFactory.prototype._delete_dict_keys = function(proxy) {
    /* Delete all keys of a previously used dict proxy. */
    var index, keys;

    keys = Object.keys(proxy);
    for (index in keys) {
        delete proxy[keys[index]];
    }
};

jigna.ProxyFactory.prototype._populate_dict_proxy = function(proxy, info) {
    var index;

    for (index in info.keys) {
        this._add_item_attribute(proxy, info.keys[index]);
    }
};

jigna.ProxyFactory.prototype._update_dict_proxy = function(proxy, info) {
    proxy.__cache__ = {}
    this._delete_dict_keys(proxy);
    this._populate_dict_proxy(proxy, info);
};

// List proxy creation /////////////////////////////////////////////////////////

jigna.ProxyFactory.prototype._create_list_proxy = function(id, info) {
    var proxy = new jigna.ListProxy('list', id, this._client);
    this._populate_list_proxy(proxy, info);

    return proxy;
};

jigna.ProxyFactory.prototype._delete_list_items = function(proxy) {
    /* Delete all items of a previously used list proxy. */

    for (var index=proxy.length-1; index >= 0; index--) {
        delete proxy[index];
    }
};

jigna.ProxyFactory.prototype._populate_list_proxy = function(proxy, info) {
    /* Populate the items in a list proxy. */

    for (var index=0; index < info.length; index++) {
        this._add_item_attribute(proxy, index);
    }

    return proxy;
};

jigna.ProxyFactory.prototype._update_list_proxy = function(proxy, info) {
    /* Update the given proxy.
     *
     * This removes all previous items and then repopulates the proxy with
     * items that reflect the (possibly) new length.
     */
    this._delete_list_items(proxy);
    this._populate_list_proxy(proxy, info);

    // Get rid of any cached items (items we have already requested from the
    // server-side.
    proxy.__cache__ = []
};

// Common for list and dict proxies ////////////////////////////////////////////

jigna.ProxyFactory.prototype._add_item_attribute = function(proxy, index){
    var descriptor, get, set;

    get = function() {
        // In here, 'this' refers to the proxy!
        var value = this.__cache__[index];
        if (value === undefined) {
            value = this.__client__.get_attribute(this, index);
            this.__cache__[index] = value;
        }

        return value;
    };

    set = function(value) {
        // In here, 'this' refers to the proxy!
        this.__cache__[index] = value;
        this.__client__.set_item(this.__id__, index, value);
    };

    descriptor = {enumerable:true, get:get, set:set, configurable:true};
    Object.defineProperty(proxy, index, descriptor);
};
