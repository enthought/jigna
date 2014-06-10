///////////////////////////////////////////////////////////////////////////////
// ProxyFactory
///////////////////////////////////////////////////////////////////////////////

define(['event_target', 'proxy', 'list_proxy'],
       function(event_target, Proxy, ListProxy){

    var ProxyFactory = function(client) {
        // Private protocol.
        this._client = client;
    };

    ProxyFactory.prototype.create_proxy = function(type, obj, info) {
        /* Create a proxy for the given type and value. */

        var factory_method = this['_create_' + type + '_proxy'];
        if (factory_method === undefined) {
            throw 'cannot create proxy for: ' + type;
        }
        return factory_method.apply(this, [obj, info]);
    };

    // Private protocol //////////////////////////////////////////////////////////

    ProxyFactory.prototype._add_item_attribute = function(proxy, index){
        var descriptor, get, set;

        get = function() {
            return this.__client__.get_attribute(this, index);
        };

        set = function(value) {
            // In here, 'this' refers to the proxy!
            this.__cache__[index] = value;
            this.__client__.set_item(this.__id__, index, value);
        };

        descriptor = {enumerable:true, get:get, set:set};
        console.log("defining index property for index:", index);
        Object.defineProperty(proxy, index, descriptor);
    };

    ProxyFactory.prototype._add_instance_method = function(proxy, method_name){
        proxy[method_name] = function() {
            // In here, 'this' refers to the proxy!
            var args = Array.prototype.slice.call(arguments);
            return this.__client__.call_instance_method(
                this.__id__, method_name, args
            );
        };
    };

    ProxyFactory.prototype._add_instance_attribute = function(proxy, attribute_name){
        var descriptor, get, set;

        get = function() {
            // In here, 'this' refers to the proxy!
            return this.__client__.get_attribute(this, attribute_name);
        };

        set = function(value) {
            // In here, 'this' refers to the proxy!
            //
            // If the proxy is for a 'HasTraits' instance then we don't need
            // to set the cached value here as the value will get updated when
            // we get the corresponsing trait event. However, setting the value
            // here means that we can create jigna UIs for non-traits objects - it
            // just means we won't react to external changes to the model(s).
            this.__cache__[attribute_name] = value;
            this.__client__.set_instance_attribute(
                this.__id__, attribute_name, value
            );
        };

        descriptor = {enumerable:true, get:get, set:set};
        Object.defineProperty(proxy, attribute_name, descriptor);

        event_target.add_listener(
            proxy,
            attribute_name,
            this._client.on_object_changed,
            this._client
        );
    };

    ProxyFactory.prototype._add_instance_event = function(proxy, event_name){
        var descriptor, set;

        set = function(value) {
            this.__cache__[event_name] = value;
            this.__client__.set_instance_attribute(
                this.__id__, event_name, value
            );
        };

        descriptor = {enumerable:false, set:set};
        Object.defineProperty(proxy, event_name, descriptor);

        event_target.add_listener(
            proxy,
            event_name,
            this._client.on_object_changed,
            this._client
        );
    };

    ProxyFactory.prototype._create_dict_proxy = function(id, info) {
        var index;

        var proxy = new Proxy('dict', id, this._client);

        for (index in info.keys) {
            this._add_item_attribute(proxy, info.keys[index]);
        }
        return proxy;
    };

    ProxyFactory.prototype._create_instance_proxy = function(id, info) {
        var index, proxy;

        proxy = new Proxy('instance', id, this._client);

        for (index in info.attribute_names) {
            this._add_instance_attribute(proxy, info.attribute_names[index]);
        }

        for (index in info.event_names) {
            this._add_instance_event(proxy, info.event_names[index]);
        }

        for (index in info.method_names) {
            this._add_instance_method(proxy, info.method_names[index]);
        }

        // This property is not actually used by jigna itself. It is only there to
        // make it easy to see what the type of the server-side object is when
        // debugging the JS code in the web inspector.
        Object.defineProperty(proxy, '__type_name__', {value : info.type_name});

        return proxy;
    };

    ProxyFactory.prototype._create_list_proxy = function(id, info) {
        var index, proxy;

        proxy = new ListProxy('list', id, this._client);

        console.log("list proxy:", proxy);

        for (index=0; index < info.length; index++) {
            this._add_item_attribute(proxy, index);
        }

        return proxy;
    };

    return ProxyFactory;
});
