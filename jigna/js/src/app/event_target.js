///// EventTarget /////////////////////////////////////////////////////////////
// Copyright (c) 2010 Nicholas C. Zakas. All rights reserved.
// MIT License
///////////////////////////////////////////////////////////////////////////////

var EventTarget = function(){
    this._listeners = {};
};

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
