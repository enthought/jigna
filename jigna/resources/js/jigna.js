///// EventTarget /////////////////////////////////////////////////////////////
// Copyright (c) 2010 Nicholas C. Zakas. All rights reserved.
// MIT License
///////////////////////////////////////////////////////////////////////////////

function EventTarget(){
    this._listeners = {};
}

EventTarget.prototype = {

    constructor: EventTarget,

    addListener: function(type, listener, thisArg){
        if (typeof this._listeners[type] == "undefined"){
            this._listeners[type] = [];
        }

        this._listeners[type].push({thisArg: thisArg || this, listener: listener});
    },

    fire: function(event){
        if (typeof event == "string"){
            event = { type: event };
        }
        if (!event.target){
            event.target = this;
        }

        if (!event.type){  //falsy
            throw new Error("Event object missing 'type' property.");
        }

        if (this._listeners[event.type] instanceof Array){
            var listeners = this._listeners[event.type];
            for (var i=0, len=listeners.length; i < len; i++){
                listener = listeners[i].listener;
                thisArg = listeners[i].thisArg;
                console.log('firing event, calling listener', event, thisArg);
                listener.call(thisArg, event);
            }
        }
    },

    removeListener: function(type, listener){
        if (this._listeners[type] instanceof Array){
            var listeners = this._listeners[type];
            for (var i=0, len=listeners.length; i < len; i++){
                if (listeners[i] === listener){
                    listeners.splice(i, 1);
                    break;
                }
            }
        }
    }
};

// SubArray.js ////////////////////////////////////////////////////////////////
// (C) Copyright Juriy Zaytsev
// Source: 1. https://github.com/kangax/array_subclassing
//         2. http://perfectionkills.com/how-ecmascript-5-still-does-not-allow-
//            to-subclass-an-array/
///////////////////////////////////////////////////////////////////////////////


var makeSubArray = (function(){

  var MAX_SIGNED_INT_VALUE = Math.pow(2, 32) - 1,
      hasOwnProperty = Object.prototype.hasOwnProperty;

  function ToUint32(value) {
    return value >>> 0;
  }

  function getMaxIndexProperty(object) {
    var maxIndex = -1, isValidProperty;

    for (var prop in object) {

      isValidProperty = (
        String(ToUint32(prop)) === prop &&
        ToUint32(prop) !== MAX_SIGNED_INT_VALUE &&
        hasOwnProperty.call(object, prop));

      if (isValidProperty && prop > maxIndex) {
        maxIndex = prop;
      }
    }
    return maxIndex;
  }

  return function(methods) {
    var length = 0;
    methods = methods || { };

    methods.length = {
      get: function() {
        var maxIndexProperty = +getMaxIndexProperty(this);
        return Math.max(length, maxIndexProperty + 1);
      },
      set: function(value) {
        var constrainedValue = ToUint32(value);
        if (constrainedValue !== +value) {
          throw new RangeError();
        }
        for (var i = constrainedValue, len = this.length; i < len; i++) {
          delete this[i];
        }
        length = constrainedValue;
      }
    };
    methods.toString = {
      value: Array.prototype.join
    };
    return Object.create(Array.prototype, methods);
  };
})();

function SubArray() {
  var arr = makeSubArray();
  if (arguments.length === 1) {
    arr.length = arguments[0];
  }
  else {
    arr.push.apply(arr, arguments);
  }
  return arr;
}

///////////////////////////////////////////////////////////////////////////////
// Enthought product code
//
// (C) Copyright 2013 Enthought, Inc., Austin, TX
// All right reserved.
//
// This file is confidential and NOT open source.  Do not distribute.
///////////////////////////////////////////////////////////////////////////////

// Namespace for all Jigna-related objects.
var jigna = {
    models : {},
    event_target : new EventTarget()
};

jigna.initialize = function() {
    // This is where all the work is done!
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

jigna.QtBridge.prototype.send_request = function(jsonized_request, callback) {
    /* Send a request to the server and wait for the reply. */

    callback(this._qt_bridge.handle_request(jsonized_request));
};

jigna.QtBridge.prototype.send_request_async = function(jsonized_request) {
    /* Send a request to the server and wait for the reply. */

    var deferred = new $.Deferred();

    var future_id = this._qt_bridge.handle_request_async(jsonized_request);

    jigna.event_target.addListener(
        '_future_updated',
        function(event){
            console.log("future updated", event, future_id);
            if (event.future_id != future_id) {
                return
            }

            else {
                if (event.status == 'done') {
                    deferred.resolve(event.result);
                }
                else if (event.status == 'error') {
                    console.log("error occured", event.result);
                    deferred.reject(event.result);
                }

                // remove the event listener
                this.removeListener('future_updated', arguments.callee)
            }
        }
    )

    return deferred
};

///////////////////////////////////////////////////////////////////////////////
// WebBridge
///////////////////////////////////////////////////////////////////////////////

jigna.WebBridge = function(client) {
    this._client = client;

    // The jigna_server attribute can be set by a client to point to a
    // different Jigna server.
    var jigna_server = window['jigna_server'];
    if (jigna_server === undefined) {
        jigna_server = window.location.host;
    }
    this._server_url = 'http://' + jigna_server;

    var url = 'ws://' + jigna_server + '/_jigna_ws';

    this._web_socket = new WebSocket(url);

    var bridge = this;
    this._web_socket.onmessage = function(event) {
        bridge.handle_event(event.data);
    };
};

jigna.WebBridge.prototype.handle_event = function(jsonized_event) {
    /* Handle an event from the server. */
    this._client.handle_event(jsonized_event);
};


jigna.WebBridge.prototype.send_request = function(jsonized_request, callback) {
    /* Send a request to the server and wait for the reply. */

    var jsonized_response;

    $.ajax(
        {
            url     : '/_jigna',
            type    : 'GET',
            data    : {'data': jsonized_request},
            success : function(result) {jsonized_response = result;},
            error   : function(status, error) {
                          console.warning("Error: " + error);
                      },
            async   : false
        }
    );

    callback(jsonized_response);
};

///////////////////////////////////////////////////////////////////////////////
// Client
///////////////////////////////////////////////////////////////////////////////

jigna.Client = function() {
    // Client protocol.
    this.bridge       = this._get_bridge();

    // Private protocol
    this._id_to_proxy_map = {};
    this._proxy_factory   = new jigna.ProxyFactory(this);

    // Add event handler for '_object_changed' and '_event_fired' events
    jigna.event_target.addListener(
        '_object_changed',
        this._on_object_changed,
        this
    );
    jigna.event_target.addListener(
        '_event_trait_fired',
        this._on_event_trait_fired,
        this
    );
    jigna.event_target.addListener(
        '_context_updated',
        this._on_context_updated,
        this
    );

    // Fire a '_context_updated' event to setup the initial context.
    var fire_context_updated = function(result) {
        jigna.event_target.fire({
            type: '_context_updated',
            data: result,
        });
    };
    this.get_context(fire_context_updated);
};

jigna.Client.prototype.handle_event = function(jsonized_event) {
    /* Handle an event from the server. */
    var event = JSON.parse(jsonized_event);

    jigna.event_target.fire(event);
};

jigna.Client.prototype.send_request = function(request, on_done) {
    /* Send a request to the server and wait for (and return) the response. */

    var jsonized_request;

    jsonized_request  = JSON.stringify(request);

    var callback = function(jsonized_response) {
        var response = JSON.parse(jsonized_response);
        if (on_done !== undefined) {
            on_done(response);
        }
    }

    this.bridge.send_request(jsonized_request, callback);
};

jigna.Client.prototype.send_request_async = function(request) {
    /* Send a request to the server and wait for (and return) the response. */

    var jsonized_request, deferred;

    jsonized_request  = JSON.stringify(request);
    deferred = this.bridge.send_request_async(jsonized_request);

    return deferred
};

// Convenience methods for each kind of request //////////////////////////////

jigna.Client.prototype.call_instance_method = function(id, method_name, async, callback, args) {
    var request = {
        kind        : 'call_instance_method',
        id          : id,
        method_name : method_name,
        args        : this._marshal_all(args)
    };

    console.log('request', request);

    if (!async) {
        client = this;
        var on_return = function(response) {
            client._unmarshal(response.result, callback);
        }
        this.send_request(request, on_return);
    }
    else {
        return this.send_request_async(request)
    }
};

jigna.Client.prototype.get_context = function(callback) {
    var request  = {kind : 'get_context'};

    var on_response = function(response) {
        callback(response.result);
    }
    this.send_request(request, on_response);
};

jigna.Client.prototype.get_dict_info = function(id, callback) {
    var request = {kind : 'get_dict_info', id : id};

    var on_response = function(response) {
        callback(response.result);
    }
    this.send_request(request, on_response);
};

jigna.Client.prototype.get_instance_attribute = function(id, attribute_name, on_result) {
    var request = {
        kind           : 'get_instance_attribute',
        id             : id,
        attribute_name : attribute_name
    };

    var client = this;

    var callback = function(response) {
        client._unmarshal(response.result, function(result) {
                on_result(result);
                if (client.bridge_mode === 'async') {
                    jigna.event_target.fire({
                        type: 'object_changed'
                    });
                }
            }
        );
    };

    this.send_request(request, callback)
};

jigna.Client.prototype.get_instance_info = function(id, on_result) {

    var request = {kind : 'get_instance_info', id : id};

    this.send_request(request, function(response) {
            on_result(response.result);
        }
    );
};

jigna.Client.prototype.get_item = function(id, index, on_result) {
    var request = {
        kind  : 'get_item',
        id    : id,
        index : index,
    };

    var client = this;
    var callback = function(response) {
        client._unmarshal(response.result, function(result) {
                on_result(result);
                if (client.bridge_mode === 'async') {
                    jigna.event_target.fire({
                        type: 'object_changed'
                    });
                }
            }
        );
    };
    this.send_request(request, callback)
};

jigna.Client.prototype.get_list_info = function(id, on_result) {
    var request = {kind : 'get_list_info', id : id};

    this.send_request(request, function(response) {
            on_result(response.result);
        }
    );
};

jigna.Client.prototype.set_instance_attribute = function(id, attribute_name, value) {
    var request = {
        kind           : 'set_instance_attribute',
        id             : id,
        attribute_name : attribute_name,
        value          : this._marshal(value)
    };

    this.send_request(request)
};

jigna.Client.prototype.set_item = function(id, index, value) {
    var request = {
        kind  : 'set_item',
        id    : id,
        index : index,
        value : this._marshal(value)
    };

    this.send_request(request)
};

// Private protocol //////////////////////////////////////////////////////////

jigna.Client.prototype._add_model = function(model_name, id, callback) {
    var proxy;

    // Expose created proxy with the name 'model_name' to the JS framework.
    var on_create = function(proxy) {
        jigna.models[model_name] = proxy;
        if (callback !== undefined) {
            callback(proxy);
        }
    }

    // Create a proxy for the object identified by the Id...
    this._create_proxy('instance', id, on_create);
};

jigna.Client.prototype._add_models = function(context, callback) {
    var model_name;
    var total = Object.keys(context).length;
    var new_proxies = [];
    for (model_name in context) {
        var on_added_model = function(proxy) {
            new_proxies.push(proxy);
            if (new_proxies.length == total) {
                if (callback !== undefined) {
                    callback(new_proxies);
                }
            }
        }
        this._add_model(model_name, context[model_name], on_added_model);
    }
};

jigna.Client.prototype._create_proxy = function(type, obj, on_create) {
    var proxy;

    if (type === 'primitive') {
        on_create(obj);
    }
    else {
        var client = this;
        var callback = function(proxy) {
            client._id_to_proxy_map[obj] = proxy;
            on_create(proxy);
        }
        this._proxy_factory.create_proxy(type, obj, callback);
    }
};

jigna.Client.prototype._get_bridge = function() {
    var bridge, qt_bridge;

    // Are we using the intra-process Qt Bridge...
    qt_bridge = window['qt_bridge'];
    if (qt_bridge !== undefined) {
        bridge = new jigna.QtBridge(this, qt_bridge);
        this.bridge_mode = 'sync';
    // ... or the inter-process web bridge?
    } else {
        bridge = new jigna.WebBridge(this);
        this.bridge_mode = 'async';
    }

    return bridge;
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

jigna.Client.prototype._unmarshal = function(obj, callback) {

    if (obj.type === 'primitive') {
        callback(obj.value);
    } else {
        value = this._id_to_proxy_map[obj.value];
        if (value === undefined) {
            this._create_proxy(obj.type, obj.value, callback);
        }
        else {
            callback(value);
        }
    }

};

jigna.Client.prototype._unmarshal_all = function(objs, callback) {
    var index;
    var count = 0;
    for (index in objs) {
        var on_unmarshal = function(value) {
            objs[index] = value;
            count += 1;
            if (count == objs.length) {
                callback(objs);
            }
        }
        this._unmarshal(objs[index], on_unmarshal);
    }
};

jigna.Client.prototype._on_object_changed = function(event) {
    this._invalidate_cached_attribute(event.obj, event.attribute_name);

    // fixme: This smells... It is used when we have a list of instances but it
    // blows away caching advantages. Can we make it smarter by managing the
    // details of a TraitListEvent?
    var on_new_proxy = function(new_proxy) {
        jigna.event_target.fire({
            type: 'object_changed'
        });
    };
    this._create_proxy(event.new_obj.type, event.new_obj.value, on_new_proxy);
};

jigna.Client.prototype._on_event_trait_fired = function(event) {
    obj_proxy = this._id_to_proxy_map[event.obj];

    var on_new_proxy = function(data_proxy) {
        jigna.event_target.fire({
            type: 'event_trait_fired',
            obj: obj_proxy,
            attribute_name: event.attribute_name,
            data: data_proxy,
        });
    };
    this._create_proxy(event.data.type, event.data.value, on_new_proxy);

};

jigna.Client.prototype._on_context_updated = function(event) {
    var on_added = function() {
        jigna.event_target.fire({
            type: 'context_updated',
            data: event.data,
        });
    };

    this._add_models(event.data, on_added);

};


///////////////////////////////////////////////////////////////////////////////
// ProxyFactory
///////////////////////////////////////////////////////////////////////////////

jigna.ProxyFactory = function(client) {
    // Private protocol.
    this._client = client;
};

jigna.ProxyFactory.prototype.create_proxy = function(type, obj, on_create) {
    /* Create a proxy for the given type and value. */

    var factory_method = this['_create_' + type + '_proxy'];
    if (factory_method === undefined) {
        throw 'cannot create proxy for: ' + type;
    }
    factory_method.apply(this, [obj, on_create]);
};

// Private protocol //////////////////////////////////////////////////////////

jigna.ProxyFactory.prototype._add_item_attribute = function(proxy, index){
    var descriptor, get, set;

    get = function() {
        var value;
        var cached_value = this.__cache__[index];
        if (cached_value !== undefined) {
            value = cached_value;
        }
        else {
            // In here, 'this' refers to the proxy!
            console.log("getter for index:", index);
            var p = this;
            var on_client_get_item = function(result) {
                p[index] = result;
                p.__cache__[index] = result;
            };
            this.__client__.get_item(this.__id__, index, on_client_get_item);
            value = this[index];
        }
        return value;
    };

    set = function(value) {
        // In here, 'this' refers to the proxy!
        this.__cache__[index] = value;
        this.__client__.set_item(this.__id__, index, value);
    };

    descriptor = {enumerable:true, get:get, set:set};
    console.log("defining index property for index:", index)
    Object.defineProperty(proxy, index, descriptor);
};

jigna.ProxyFactory.prototype._add_instance_method = function(proxy, method_name){
    var method = function (async, callback, args) {
        return this.__client__.call_instance_method(
            this.__id__, method_name, async, callback, args
        );
    };

    proxy[method_name] = function(callback) {
        // In here, 'this' refers to the proxy!
        var args = Array.prototype.slice.call(arguments, 1);
        method.call(this, false, callback, args);
    };

    proxy[method_name+"_async"] = function(){
        // In here, 'this' refers to the proxy!
        var args = Array.prototype.slice.call(arguments);

        return method.call(this, true, args);
    };
};

jigna.ProxyFactory.prototype._add_instance_attribute = function(proxy, attribute_name){
    var descriptor, get, set;

    get = function() {
        // In here, 'this' refers to the proxy!
        var cached_value, value;

        cached_value = this.__cache__[attribute_name];
        if (cached_value !== undefined) {
            value = cached_value;

        } else {
            var p = this;
            var on_result = function(result) {
                p.__cache__[attribute_name] = result;
            };

            this.__client__.get_instance_attribute(
                this.__id__, attribute_name, on_result
            );
            // In the async case, this will be up-to-date.
            value = this.__cache__[attribute_name];
        }

        return value;
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
};

jigna.ProxyFactory.prototype._create_dict_proxy = function(id, on_create) {

    var proxy_factory = this;
    var on_dict_info = function(info) {
        var index, proxy;

        proxy = new jigna.Proxy('dict', id, proxy_factory._client);

        for (index in info.keys) {
            proxy_factory._add_item_attribute(proxy, info.keys[index]);
        }
        on_create(proxy);
    };

    this._client.get_dict_info(id, on_dict_info);
};

jigna.ProxyFactory.prototype._create_instance_proxy = function(id, on_create) {
    var proxy_factory = this;
    var on_get_instance_info = function(info) {
        var index, proxy;

        proxy = new jigna.Proxy('instance', id, proxy_factory._client);

        for (index in info.attribute_names) {
            proxy_factory._add_instance_attribute(proxy, info.attribute_names[index]);
        }

        for (index in info.method_names) {
            proxy_factory._add_instance_method(proxy, info.method_names[index]);
        }

        // This property is not actually used by jigna itself. It is only there to
        // make it easy to see what the type of the server-side object is when
        // debugging the JS code in the web inspector.
        Object.defineProperty(proxy, '__type_name__', {value : info.type_name});

        on_create(proxy);
    };

    this._client.get_instance_info(id, on_get_instance_info);
};

jigna.ProxyFactory.prototype._create_list_proxy = function(id, on_create) {
    var proxy_factory = this;
    var on_get_list_info = function(info) {
        var index, proxy;

        proxy = new jigna.ListProxy('list', id, proxy_factory._client);

        console.log("list proxy:", proxy);

        for (index=0; index < info.length; index++) {
            proxy_factory._add_item_attribute(proxy, index);
        }

        console.log("list proxy after property addition:", proxy);
        on_create(proxy);
    }

    this._client.get_list_info(id, on_get_list_info);

};

///////////////////////////////////////////////////////////////////////////////
// Proxies
///////////////////////////////////////////////////////////////////////////////

jigna.Proxy = function(type, id, client) {
    // We use the '__attribute__' pattern to reduce the risk of name clashes
    // with the actuall attribute and methods on the object that we are a
    // proxy for.
    Object.defineProperty(this, '__type__',   {value : type});
    Object.defineProperty(this, '__id__',     {value : id});
    Object.defineProperty(this, '__client__', {value : client});
    Object.defineProperty(this, '__cache__',  {value : {}});
};

// ListProxy is handled separately because it has to do special handling
// to behave as regular Javascript `Array` objects
// See "Wrappers. Prototype chain injection" section in this article:
// http://perfectionkills.com/how-ecmascript-5-still-does-not-allow-to-subclass-an-array/

jigna.ListProxy = function(type, id, client) {

    var arr = new SubArray();

    // fixme: repetition of property definition
    Object.defineProperty(arr, '__type__',   {value : type});
    Object.defineProperty(arr, '__id__',     {value : id});
    Object.defineProperty(arr, '__client__', {value : client});
    Object.defineProperty(arr, '__cache__',  {value : []});

    return arr;
}

///////////////////////////////////////////////////////////////////////////////
// Auto-initialization
///////////////////////////////////////////////////////////////////////////////

jigna.initialize();

///////////////////////////////////////////////////////////////////////////////
// AngularJS
///////////////////////////////////////////////////////////////////////////////

var module = angular.module('jigna', []);

// Add initialization function on module run time
module.run(function($rootScope, $compile){

    var update_scope_with_models = function(context) {
        for (var model_name in context) {
            $rootScope[model_name] = jigna.models[model_name];
        }
    }

    // Initialize the scope with the jigna models.
    update_scope_with_models(jigna.models);

    // Listen to object change events in jigna
    jigna.event_target.addListener('object_changed', function() {
        if ($rootScope.$$phase === null){
            $rootScope.$digest();
        }
    }, false);

    // Listen to 'context_updated' events in jigna and update the scope.
    jigna.event_target.addListener('context_updated', function(event) {
        update_scope_with_models(event.data);
    }, false);

    // A method that allows us to recompile a part of the document after
    // DOM modifications.  For example one could have:
    //
    // var new_elem = $("<input ng-model='model.name'>");
    // $("#some-element").append(new_elem);
    // scope.recompile(new_elem);
    //
    $rootScope.recompile = function(element) {
        $compile(element)($rootScope);
        if ($rootScope.$$phase === null){
            $rootScope.$digest();
        }
    };

})

// EOF ////////////////////////////////////////////////////////////////////////
