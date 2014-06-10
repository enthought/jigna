///////////////////////////////////////////////////////////////////////////////
// Client
///////////////////////////////////////////////////////////////////////////////

define(['proxy_factory', 'event_target', 'qt_bridge', 'web_bridge', 'proxy'],
function(ProxyFactory, event_target, QtBridge, WebBridge, Proxy){

    var Client = function() {};

    Client.prototype.initialize = function() {
        // Client protocol.
        this.bridge           = this._get_bridge();

        this._id_to_proxy_map = {};
        this._proxy_factory   = new ProxyFactory(this);

        // Add all of the models being edited
        event_target.add_listener(
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

    Client.prototype.handle_event = function(jsonized_event) {
        /* Handle an event from the server. */
        var event = JSON.parse(jsonized_event);

        event_target.fire_event(event.obj, event);
    };

    Client.prototype.on_object_changed = function(event){
        this._invalidate_cached_attribute(event.obj, event.name);

        // fixme: Creating a new proxy smells... It is used when we have a list of
        // instances but it blows away caching advantages. Can we make it smarter
        // by managing the details of a TraitListEvent?

        var data = event.data;
        this._create_proxy(data.type, data.value, data.info);
        event_target.fire_event('jigna', 'object_changed');
    };

    Client.prototype.send_request = function(request) {
        /* Send a request to the server and wait for (and return) the response. */

        var jsonized_request  = JSON.stringify(request);
        var jsonized_response = this.bridge.send_request(jsonized_request);

        return JSON.parse(jsonized_response).result;
    };

    // Convenience methods for each kind of request //////////////////////////////

    Client.prototype.call_instance_method = function(id, method_name, args) {
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

    Client.prototype.call_instance_method_thread = function(id, method_name, args) {
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

        event_target.add_listener(future_obj, 'done', function(event){
            deferred.resolve(event.data);
        });

        event_target.add_listener(future_obj, 'error', function(event){
            deferred.reject(event.data);
        });

        return deferred.promise();
    };

    Client.prototype.get_attribute_from_server = function(proxy, attribute) {
        /* Get the specified attribute of the proxy from the server. */

        var request = this._create_request(proxy, attribute);

        var response = this.send_request(request);
        var result = this._unmarshal(response);

        return result;
    };

    Client.prototype.get_attribute = function(proxy, attribute) {
        /* Get the specified attribute of the proxy. If a cached value is
        available, return that; otherwise get it from the server. */
        var value;
        var cached_value = proxy.__cache__[attribute];

        if (cached_value === undefined) {
            // Get it from the server.
            value = this.get_attribute_from_server(proxy, attribute);
            proxy.__cache__[attribute] = value;
        }
        else {
            value = cached_value;
        }

        return value;
    };

    Client.prototype.set_instance_attribute = function(id, attribute_name, value) {
        var request = {
            kind           : 'set_instance_attribute',
            id             : id,
            attribute_name : attribute_name,
            value          : this._marshal(value)
        };

        this.send_request(request);
    };

    Client.prototype.set_item = function(id, index, value) {
        var request = {
            kind  : 'set_item',
            id    : id,
            index : index,
            value : this._marshal(value)
        };

        this.send_request(request);
    };

    Client.prototype.update_context = function() {
        var request  = {kind : 'update_context'};

        this.send_request(request);
    };

    // Private protocol //////////////////////////////////////////////////////////

    Client.prototype._add_model = function(model_name, id, info) {
        // Create a proxy for the object identified by the Id...
        var proxy = this._create_proxy('instance', id, info);

        // fire the event to let the UI toolkit know that a new model was added
        var data = {};
        data[model_name] = proxy;

        event_target.fire_event('jigna', {
            name: 'model_added',
            data: data,
        });

        return proxy;
    };

    Client.prototype._add_models = function(context) {
        var client = this;
        var models = {};
        $.each(context, function(model_name, model) {
            proxy = client._add_model(model_name, model.value, model.info);
            models[model_name] = proxy;
        });

        return models;
    };

    Client.prototype._create_proxy = function(type, obj, info) {
        if (type === 'primitive') {
            return obj;
        }
        else {
            var proxy = this._proxy_factory.create_proxy(type, obj, info);
            this._id_to_proxy_map[obj] = proxy;
            return proxy;
        }
    };

    Client.prototype._get_bridge = function() {
        var bridge, qt_bridge;

        // Are we using the intra-process Qt Bridge...
        qt_bridge = window['qt_bridge'];
        if (qt_bridge !== undefined) {
            bridge = new QtBridge(this, qt_bridge);
        // ... or the inter-process web bridge?
        } else {
            bridge = new WebBridge(this);
        }

        return bridge;
    };

    Client.prototype._create_request = function(proxy, attribute) {
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

    Client.prototype._invalidate_cached_attribute = function(id, attribute_name) {
        var proxy = this._id_to_proxy_map[id];
        proxy.__cache__[attribute_name] = undefined;
    };

    Client.prototype._marshal = function(obj) {
        var type, value;

        if (obj instanceof Proxy) {
            type  = obj.__type__;
            value = obj.__id__;

        } else {
            type  = 'primitive';
            value = obj;
        }

        return {'type' : type, 'value' : value};
    };

    Client.prototype._marshal_all = function(objs) {
        var index;

        for (index in objs) {
            objs[index] = this._marshal(objs[index]);
        }

        // For convenience, as we modify the array in-place.
        return objs;
    };

    Client.prototype._unmarshal = function(obj) {

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

    return Client;
});
