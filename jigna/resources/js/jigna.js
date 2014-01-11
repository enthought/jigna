///// EventTarget /////////////////////////////////////////////////////////////
// Copyright (c) 2010 Nicholas C. Zakas. All rights reserved.
// MIT License
///////////////////////////////////////////////////////////////////////////////

function EventTarget(){
    this._listeners = {};
}

EventTarget.prototype = {

    constructor: EventTarget,

    add_listener: function(obj, event_name, listener, thisArg){
        var id = this._to_id(obj);

        if (this._listeners[id] === undefined){
            this._listeners[id] = {};
        }

        if (this._listeners[id][event_name] === undefined) {
            this._listeners[id][event_name] = [];
        }

        this._listeners[id][event_name].push({thisArg: thisArg, listener: listener});
    },

    fire_event: function(obj, event){
        var id = this._to_id(obj);

        if (typeof event == "string"){
            event = { name: event };
        }
        if (!event.target){
            event.target = obj;
        }

        if (!event.name){  //falsy
            console.log('event:', event);
            throw new Error("Event object missing 'name' property.");
        }

        if (this._listeners[id] === undefined) {
            return;
        }

        if (this._listeners[id][event.name] instanceof Array){
            var listeners = this._listeners[id][event.name];
            for (var i=0, len=listeners.length; i < len; i++){
                listener = listeners[i].listener;
                thisArg = listeners[i].thisArg;
                listener.call(thisArg, event);
            }
        }
    },

    remove_listener: function(obj, event_name, listener){
        var id = this._to_id(obj);

        if (this._listeners[id][event_name] instanceof Array){
            var listeners = this._listeners[id][event_name];
            for (var i=0, len=listeners.length; i < len; i++){
                if (listeners[i] === listener){
                    listeners.splice(i, 1);
                    break;
                }
            }
        }
    },

    //// Private protocol /////////////////////////////////////////////////////

    _to_id: function(obj){
        if (obj.__id__ !== undefined) {
            return obj.__id__;
        }
        else {
            return obj;
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
var jigna = new EventTarget();

jigna.initialize = function() {
    // Determine if jigna is to run async or sync.  This can be set
    // by setting window.jigna_async to true or false.  The jigna.async
    // option can also be changed at runtime.  Async is meaningful only with
    // the web bridge.
    this.async = false;
    if (window.jigna_async !== undefined) {
        this.async = window.jigna_async;
    }
    this.models = {};
    // This is where all the work is done!
    this.client = new jigna.Client();
};

// A convenience function to get a particular expression once it is really
// set.  This returns a promise object.
// Arguments:
//   - expr a javascript expression to evaluate,
//   - timeout (optional) in seconds; defaults to 2 seconds,
jigna.get_attribute = function (expr, timeout, deferred) {
    if (timeout === undefined) {
        timeout = 2;
    }
    if (deferred === undefined) {
        deferred = new $.Deferred();
    }

    var wait = 100;
    var result;
    try {
        result = eval(expr);
    }
    catch(err) {
        result = undefined;
        if (timeout <= 0) {
            deferred.reject(err);
        }
    }
    if (result === undefined) {
        if (timeout <= 0) {
            deferred.reject("Timeout exceeded while waiting for expression: " + expr);
        }
        setTimeout(function() {
                jigna.get_attribute(expr, (timeout*1000 - wait)/1000., deferred);
            }, wait
        );
    }
    else {
        deferred.resolve(result);
    }
    return deferred.promise();
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

    var deferred = new $.Deferred();
    deferred.resolve(this._qt_bridge.handle_request(jsonized_request));
    return deferred.promise();
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

    this._messages = {};
    this._message_count = 0;

    this._web_socket = new WebSocket(url);
    this._ws_opened = new $.Deferred();
    var bridge = this;
    this._web_socket.onopen = function() {
        bridge._ws_opened.resolve();
    }
    this._web_socket.onmessage = function(event) {
        bridge.handle_event(event.data);
    };
};

jigna.WebBridge.prototype.handle_event = function(jsonized_event) {
    /* Handle an event from the server. */
    var response = JSON.parse(jsonized_event);
    var message_id = response[0];
    var jsonized_response = response[1];
    if (message_id === -1) {
        this._client.handle_event(jsonized_response);
    }
    else {
        var deferred = this._messages[message_id];
        deferred.resolve(jsonized_response);
        delete this._messages[message_id];
    }
};

jigna.WebBridge.prototype._get_message_id = function() {
    var id = this._message_count;
    if (id > 1048576) {
        this._message_count = 0;
    }
    this._message_count += 1;
    return id;
};

jigna.WebBridge.prototype.send_request = function(jsonized_request) {
    if (jigna.async) {
        return this._send_request_async(jsonized_request);
    }
    else {
        return this._send_request_sync(jsonized_request);
    }
};

jigna.WebBridge.prototype._send_request_async = function(jsonized_request) {
    /* Send a request to the server and do not wait and return a Promise
       which is resolved upon completion of the request.
    */

    var message_id = this._get_message_id();
    var deferred = new $.Deferred();
    this._messages[message_id] = deferred;
    var bridge = this;
    this._ws_opened.done(function() {
        bridge._web_socket.send(JSON.stringify([message_id, jsonized_request]));
    });
    return deferred.promise();
};

jigna.WebBridge.prototype._send_request_sync = function(jsonized_request) {
    /* Send a request to the server and wait for the reply. */

    var jsonized_response;
    var deferred = new $.Deferred();

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

    deferred.resolve(jsonized_response);
    return deferred.promise();
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

    // Add all of the models being edited.
    jigna.add_listener(
        'jigna',
        'context_updated',
        function(event){ this._add_models(event.data); },
        this
    );

    // Fire a '_context_updated' event to setup the initial context.
    this.get_context().done(function(result) {
        jigna.fire_event('jigna', {
            name: 'context_updated',
            data: result,
        });
    });
};

jigna.Client.prototype.handle_event = function(jsonized_event) {
    /* Handle an event from the server. */
    var event = JSON.parse(jsonized_event);

    jigna.fire_event(event.obj, event);
};

jigna.Client.prototype.on_object_changed = function(event){
    this._invalidate_cached_attribute(event.obj, event.name);

    // fixme: Creating a new proxy smells... It is used when we have a list of
    // instances but it blows away caching advantages. Can we make it smarter
    // by managing the details of a TraitListEvent?

    var data = event.data;
    this._create_proxy(data.type, data.value, data.info);
    jigna.fire_event(jigna, 'object_changed');
};

jigna.Client.prototype.send_request = function(request) {
    /* Send a request to the server and wait for (and return) the response. */

    var jsonized_request  = JSON.stringify(request);

    var deferred = new $.Deferred();
    this.bridge.send_request(jsonized_request).done(
        function(jsonized_response) {
            deferred.resolve(JSON.parse(jsonized_response).result);
        }
    );
    return deferred.promise();
};

jigna.Client.prototype.send_request_async = function(request) {
    /* Send a request to the server and return a deferred object. */

    var jsonized_request, deferred;

    request["async"] = true;
    jsonized_request  = JSON.stringify(request);
    deferred = new $.Deferred();

    this.bridge.send_request(jsonized_request).done(
        function(future_obj) {
            jigna.add_listener(future_obj, 'done', function(event){
                deferred.resolve(event.data);
            });

            jigna.add_listener(future_obj, 'error', function(event){
                deferred.reject(event.data);
            });
        }
    );

    return deferred.promise();
};

// Convenience methods for each kind of request //////////////////////////////

jigna.Client.prototype.call_instance_method = function(id, method_name, async, args) {
    var request = {
        kind        : 'call_instance_method',
        id          : id,
        method_name : method_name,
        args        : this._marshal_all(args)
    };

    console.log('request', request);

    if (!async) {
        client = this;
        if (jigna.async) {
            var deferred = new $.Deferred();
            this.send_request(request).done(
                function(response) {
                    deferred.resolve(client._unmarshal(response));
                }
            );
            return deferred.promise();
        }
        else {
            // Synchronous case: we return the value.
            var _result;
            this.send_request(request).done(
                function(response) {
                    _result = client._unmarshal(response);
                }
            );
            return _result;
        }
    }
    else {
        return this.send_request_async(request);
    }
};

jigna.Client.prototype.get_context = function() {
    var request  = {kind : 'get_context'};

    return this.send_request(request);
};

jigna.Client.prototype.get_instance_attribute = function(id, attribute_name) {
    var request = {
        kind           : 'get_instance_attribute',
        id             : id,
        attribute_name : attribute_name
    };

    var client = this;
    var deferred = new $.Deferred();

    this.send_request(request).done(
        function(result) {
            deferred.resolve(client._unmarshal(result));
        }
    );
    return deferred.promise();
};

jigna.Client.prototype.get_item = function(id, index) {
    var request = {
        kind  : 'get_item',
        id    : id,
        index : index,
    };

    var client = this;
    var deferred = new $.Deferred();

    this.send_request(request).done(
        function(result) {
            deferred.resolve(client._unmarshal(result));
        }
    );
    return deferred.promise();
};

jigna.Client.prototype.set_instance_attribute = function(id, attribute_name, value) {
    var request = {
        kind           : 'set_instance_attribute',
        id             : id,
        attribute_name : attribute_name,
        value          : this._marshal(value)
    };

    this.send_request(request);
};

jigna.Client.prototype.set_item = function(id, index, value) {
    var request = {
        kind  : 'set_item',
        id    : id,
        index : index,
        value : this._marshal(value)
    };

    this.send_request(request);
};

// Private protocol //////////////////////////////////////////////////////////

jigna.Client.prototype._add_model = function(model_name, id, info) {
    // Create a proxy for the object identified by the Id...
    var proxy = this._create_proxy('instance', id, info);
    // Expose created proxy with the name 'model_name' to the JS framework.
    jigna.models[model_name] = proxy;
    return proxy;
};

jigna.Client.prototype._add_models = function(context) {
    var new_proxies = [];

    var client = this;
    $.each(context, function(model_name, model) {
        new_proxies.push(client._add_model(model_name, model.value, model.info))
    });
    return new_proxies;
};

jigna.Client.prototype._create_proxy = function(type, obj, info) {
    if (type === 'primitive') {
        return obj;
    }
    else {
        var proxy = this._proxy_factory.create_proxy(type, obj, info);
        this._id_to_proxy_map[obj] = proxy;
        return proxy;
    }
};

jigna.Client.prototype._get_bridge = function() {
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
    return factory_method.apply(this, [obj, info]);
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
            if (jigna.async) {
                // Set this to a sentinel value so angular does not call us a
                // million times before our real value is set.
                this.__cache__[index] = null;
            }
            var p = this;
            this.__client__.get_item(this.__id__, index).done(
                function(result) {
                    p.__cache__[index] = result;
                    if (jigna.async) {
                        jigna.fire_event(jigna, 'object_changed');
                    }
                }
            );
            value = this.__cache__[index];
        }
        if (value === null) {
            return undefined;
        }
        else {
            return value;
        }
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

jigna.ProxyFactory.prototype._add_instance_method = function(proxy, method_name){
    var method = function (async, args) {
        return this.__client__.call_instance_method(
            this.__id__, method_name, async, args
        );
    };

    proxy[method_name] = function() {
        // In here, 'this' refers to the proxy!
        var args = Array.prototype.slice.call(arguments);
        return method.call(this, false, args);
    };

    // fixme: this is ugly and potentially dangerous. Ideally we should have a
    // jigna.async(func, args) method.
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
            if (jigna.async) {
                // Set this to a sentinel value so angular does not call us a
                // million times before our real value is set.
                this.__cache__[attribute_name] = null;
            }
            var p = this;
            this.__client__.get_instance_attribute(
                this.__id__, attribute_name
            ).done(
                function(result) {
                    p.__cache__[attribute_name] = result;
                    if (jigna.async) {
                        jigna.fire_event(jigna, 'object_changed');
                    }
                }
            );
            // In the async case, this will be up-to-date.
            value = this.__cache__[attribute_name];
        }
        if (value === null) {
            return undefined;
        }
        else {
            return value;
        }
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

    jigna.add_listener(
        proxy,
        attribute_name,
        this._client.on_object_changed,
        this._client
    );
};

jigna.ProxyFactory.prototype._add_instance_event = function(proxy, event_name){
    var descriptor, set;

    set = function(value) {
        this.__cache__[event_name] = value;
        this.__client__.set_instance_attribute(
            this.__id__, event_name, value
        );
    };

    descriptor = {enumerable:false, set:set};
    Object.defineProperty(proxy, event_name, descriptor);

    jigna.add_listener(
        proxy,
        event_name,
        this._client.on_object_changed,
        this._client
    );
};

jigna.ProxyFactory.prototype._create_dict_proxy = function(id, info) {
    var index;

    var proxy = new jigna.Proxy('dict', id, this._client);

    for (index in info.keys) {
        this._add_item_attribute(proxy, info.keys[index]);
    }
    return proxy;
};

jigna.ProxyFactory.prototype._create_instance_proxy = function(id, info) {
    var index, proxy;

    proxy = new jigna.Proxy('instance', id, this._client);

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

jigna.ProxyFactory.prototype._create_list_proxy = function(id, info) {
    var index, proxy;

    proxy = new jigna.ListProxy('list', id, this._client);

    console.log("list proxy:", proxy);

    for (index=0; index < info.length; index++) {
        this._add_item_attribute(proxy, index);
    }

    console.log("list proxy after property addition:", proxy);
    return proxy;
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
};

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

    // Add all jigna models as scope variables
    var add_to_scope = function(context) {
        for (var model_name in context) {
            $rootScope[model_name] = jigna.models[model_name];
        }
        jigna.fire_event(jigna, 'object_changed');
    };

    add_to_scope(jigna.models);

    jigna.add_listener('jigna', 'context_updated', function(event){
        console.log("event.data", event.data);
        add_to_scope(event.data);
    });

    // Listen to object change events in jigna
    jigna.add_listener(jigna, 'object_changed', function() {
        if ($rootScope.$$phase === null){
            $rootScope.$digest();
        }
    });

    // fixme: this is very ugly. remove this asap.
    $rootScope.recompile = function(element) {
        $compile(element)($rootScope);

        jigna.fire_event(jigna, 'object_changed');
    };

    if (jigna.async) {
        // fixme: digesting on document.ready doesn't work and this smells.
        setTimeout(function() {jigna.fire_event(jigna, 'object_changed');}, 200);
    }
});

// EOF ////////////////////////////////////////////////////////////////////////
