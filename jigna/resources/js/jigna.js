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

    fire: function(obj, event){
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
    this.models = {};
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

jigna.QtBridge.prototype.send_request = function(jsonized_request, mode) {
    /* Send a request to the server and wait for the reply. */

    if (mode === undefined) {
        mode = "sync";
    }

    if (mode == "sync") {
        return this._qt_bridge.handle_request(jsonized_request);
    }
    else {
        return this._qt_bridge.handle_request_async(jsonized_request);
    }
};

///////////////////////////////////////////////////////////////////////////////
// WebBridge
///////////////////////////////////////////////////////////////////////////////

jigna.WebBridge = function(client) {

    // The jigna_server attribute can be set by a client to point to a
    // different Jigna server.
    var jigna_server = window['jigna_server'];
    if (jigna_server === undefined) {
        jigna_server = window.location.host;
    }
    this._server_url = 'http://' + jigna_server;

    var url = 'ws://' + jigna_server + '/_jigna_ws';

    this._web_socket = new WebSocket(url);
    this._web_socket.onmessage = function(event) {
        client.handle_event(event.data);
    };
};

jigna.WebBridge.prototype.send_request = function(jsonized_request, mode) {
    /* Send a request to the server and wait for the reply. */

    var jsonized_response;

    if (mode === undefined) {
        mode = "sync";
    }

    $.ajax(
        {
            url     : '/_jigna',
            type    : 'GET',
            data    : {'data': jsonized_request, 'mode': mode},
            success : function(result) {jsonized_response = result;},
            error   : function(status, error) {
                          console.warning("Error: " + error);
                      },
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
    
    jigna.fire('jigna', {
        name: 'context_updated',
        data: this.get_context()
    });
    
};

jigna.Client.prototype.handle_event = function(jsonized_event) {
    /* Handle an event from the server. */
    var event = JSON.parse(jsonized_event);

    jigna.fire(event.obj, event);
};

jigna.Client.prototype.on_object_changed = function(event){
    this._invalidate_cached_attribute(event.obj, event.name);

    // fixme: This smells... It is used when we have a list of instances but it
    // blows away caching advantages. Can we make it smarter by managing the
    // details of a TraitListEvent?
    this._create_proxy(event.data.type, event.data.value);

    jigna.fire(jigna, '$digest');

};

jigna.Client.prototype.send_request = function(request) {
    /* Send a request to the server and wait for (and return) the response. */

    var jsonized_request, jsonized_response, response;

    jsonized_request  = JSON.stringify(request);
    jsonized_response = this.bridge.send_request(jsonized_request);
    response          = JSON.parse(jsonized_response);

    return response;
};

jigna.Client.prototype.send_request_async = function(request) {
    /* Send a request to the server and wait for (and return) the response. */

    var jsonized_request, deferred;

    jsonized_request  = JSON.stringify(request);
    deferred = new $.Deferred();

    var future_obj = this.bridge.send_request(jsonized_request, "async");

    jigna.add_listener(future_obj, 'done', function(event){
        deferred.resolve(event.data);
    });

    jigna.add_listener(future_obj, 'error', function(event){
        deferred.reject(event.data);
    });

    return deferred;
};

// Convenience methods for each kind of request //////////////////////////////

jigna.Client.prototype.call_instance_method = function(id, method_name, async, args) {
    var request, response;

    request  = {
        kind        : 'call_instance_method',
        id          : id,
        method_name : method_name,
        args        : this._marshal_all(args)
    };

    console.log('request', request);

    if (!async) {
        response = this.send_request(request);

        return this._unmarshal(response.result);
    }
    else {
        return this.send_request_async(request);
    }
};

jigna.Client.prototype.get_context = function() {
    var request, response;

    request  = {kind : 'get_context'};
    response = this.send_request(request);

    return response.result;
};

jigna.Client.prototype.get_dict_info = function(id) {
    var request, response;

    request  = {kind : 'get_dict_info', id : id};
    response = this.send_request(request);

    return response.result;
};

jigna.Client.prototype.get_instance_attribute = function(id, attribute_name) {
    var request, response;

    request = {
        kind           : 'get_instance_attribute',
        id             : id,
        attribute_name : attribute_name
    };

    response = this.send_request(request);

    return this._unmarshal(response.result);
};

jigna.Client.prototype.get_instance_info = function(id) {
    var request, response;

    request  = {kind : 'get_instance_info', id : id};
    response = this.send_request(request);

    return response.result;
};

jigna.Client.prototype.get_item = function(id, index) {
    var request, response;

    request = {
        kind  : 'get_item',
        id    : id,
        index : index,
    };

    response = this.send_request(request);

    return this._unmarshal(response.result);
};

jigna.Client.prototype.get_list_info = function(id) {
    var request, response;

    request  = {kind : 'get_list_info', id : id};
    response = this.send_request(request);

    return response.result;
};

jigna.Client.prototype.set_instance_attribute = function(id, attribute_name, value) {
    var request;

    request = {
        kind           : 'set_instance_attribute',
        id             : id,
        attribute_name : attribute_name,
        value          : this._marshal(value)
    };

    this.send_request(request);
};

jigna.Client.prototype.set_item = function(id, index, value) {
    var request;

    request = {
        kind  : 'set_item',
        id    : id,
        index : index,
        value : this._marshal(value)
    };

    this.send_request(request);
};

// Private protocol //////////////////////////////////////////////////////////

jigna.Client.prototype._add_model = function(model_name, id) {
    var proxy;

    // Create a proxy for the object identified by the Id...
    proxy = this._create_proxy('instance', id);

    // ... and expose it with the name 'model_name' to the JS framework.
    jigna.models[model_name] = proxy;

    return proxy;
};

jigna.Client.prototype._add_models = function(context) {
    var model_name;

    for (model_name in context) {
        this._add_model(model_name, context[model_name]);
    }
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

///////////////////////////////////////////////////////////////////////////////
// ProxyFactory
///////////////////////////////////////////////////////////////////////////////

jigna.ProxyFactory = function(client) {
    // Private protocol.
    this._client = client;
};

jigna.ProxyFactory.prototype.create_proxy = function(type, obj) {
    /* Create a proxy for the given type and value. */

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
        console.log("getter for index:", index);
        return this.__client__.get_item(this.__id__, index);
    };

    set = function(value) {
        // In here, 'this' refers to the proxy!
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
            value = this.__client__.get_instance_attribute(
                this.__id__, attribute_name
            );
            this.__cache__[attribute_name] = value;
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

jigna.ProxyFactory.prototype._create_dict_proxy = function(id) {
    var index, info, proxy;

    proxy = new jigna.Proxy('dict', id, this._client);

    info = this._client.get_dict_info(id);
    for (index in info.keys) {
        this._add_item_attribute(proxy, info.keys[index]);
    }

    return proxy;
};

jigna.ProxyFactory.prototype._create_instance_proxy = function(id) {
    var index, info, proxy;

    proxy = new jigna.Proxy('instance', id, this._client);

    info = this._client.get_instance_info(id);
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

jigna.ProxyFactory.prototype._create_list_proxy = function(id) {
    var index, info, proxy;

    proxy = new jigna.ListProxy('list', id, this._client);

    console.log("list proxy:", proxy);

    info = this._client.get_list_info(id);
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
    Object.defineProperty(arr, '__cache__',  {value : {}});
    
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
    var add_to_scope = function(context){
        for (var model_name in context) {
            $rootScope[model_name] = jigna.models[model_name];
        }

        jigna.fire(jigna, '$digest');
    };
    add_to_scope(jigna.models);

    jigna.add_listener('jigna', 'context_updated', function(event){
        console.log("event.data", event.data);
        add_to_scope(event.data);
    });

    // Listen to object change events in jigna
    jigna.add_listener(jigna, '$digest', function() {
        if ($rootScope.$$phase === null){
            $rootScope.$digest();
        }
    });
});

// EOF ////////////////////////////////////////////////////////////////////////
