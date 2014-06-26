///////////////////////////////////////////////////////////////////////////////
// Jigna
///////////////////////////////////////////////////////////////////////////////

// Namespace for all Jigna-related objects.
var jigna = new EventTarget();

jigna.initialize = function(options) {
    options = options || {};
    this.client = options.async ? new jigna.AsyncClient() : new jigna.Client();
    this.client.initialize();
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

// A convenience function to get a particular expression once it is really
// set.  This returns a promise object.
// Arguments:
//   - expr a javascript expression to evaluate,
//   - timeout (optional) in seconds; defaults to 2 seconds,
jigna.wait_for = function (expr, timeout) {
    var deferred = new $.Deferred();

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

    // resolve with the obtained result if it wasn't undefined
    if (result !== undefined) {
        deferred.resolve(result);
    }
    // otherwise, try again after some time until the given timeout
    else {
        timeout = timeout || 2;
        // keep polling for the result every 100 ms or so. Keep decreasing
        // the time remaining on each call by 100 ms and break when we reach
        // 0.
        if (timeout > 0) {
            var wait = 100;
            setTimeout(function(){
                expr_loaded = jigna.wait_for(expr, (timeout*1000 - wait)/1000.0);
                expr_loaded.done(function(value){deferred.resolve(value);});
                expr_loaded.fail(function(err){deferred.reject(err);});
            }, wait);
        }
        else {
            deferred.reject("Timeout exceeded while waiting for expression: " + expr);
        }
    }

    return deferred.promise();
};
