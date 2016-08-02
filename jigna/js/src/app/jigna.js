///////////////////////////////////////////////////////////////////////////////
// Jigna
///////////////////////////////////////////////////////////////////////////////

// Namespace for all Jigna-related objects.
var jigna = new EventTarget();

jigna.initialize = function(options) {
    options = options || {};
    this.ready  = $.Deferred();
    this.debug  = options.debug;
    this.async  = options.async;
    this.client = options.async ? new jigna.AsyncClient() : new jigna.Client();
    this.client.initialize();
    return this.ready;
};

jigna.models = {};

jigna.add_listener('jigna', 'model_added', function(event){
    var models = event.data;
    for (var model_name in models) {
        jigna.models[model_name] = models[model_name];
    }

    jigna.fire_event('jigna', 'object_changed');
});

jigna.threaded = function(obj, method_name, args) {
    args = Array.prototype.slice.call(arguments, 2);
    return this.client.call_instance_method_thread(obj.__id__, method_name, args);
};
