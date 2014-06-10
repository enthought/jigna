///////////////////////////////////////////////////////////////////////////////
// Jigna
///////////////////////////////////////////////////////////////////////////////

define(['jquery', 'event_target', 'client', 'async_client'],
       function($, event_target, Client, AsyncClient){

    // Namespace for all Jigna-related objects.
    var jigna = Object.create(event_target);

    jigna.initialize = function(options) {

        options = options || {};
        this.client = options.async ? new AsyncClient() : new Client();
        this.client.initialize();
    };

    jigna.models = {};
    jigna.add_listener('jigna', 'model_added', function(event){
        var models = event.data;
        for (var model_name in models) {
            jigna.models[model_name] = models[model_name];
        }
    });

    jigna.threaded = function(obj, method_name, args) {
        args = args || [];
        return this.client.call_instance_method_thread(obj.__id__, method_name, args);
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

    return jigna;

});
