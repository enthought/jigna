///////////////////////////////////////////////////////////////////////////////
// AsyncClient
///////////////////////////////////////////////////////////////////////////////

// Inherit AsyncClient from Client
// Source: MDN docs (https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/create)
jigna.AsyncClient = function() {};
jigna.AsyncClient.prototype = Object.create(jigna.Client.prototype);
jigna.AsyncClient.prototype.constructor = jigna.AsyncClient;

jigna.AsyncClient.prototype.send_request = function(request) {
    /* Send a request to the server and wait for (and return) the response. */

    var jsonized_request  = JSON.stringify(request);

    var deferred = new $.Deferred();
    this.bridge.send_request_async(jsonized_request).done(function(jsonized_response){
        deferred.resolve(JSON.parse(jsonized_response).result);
    });

    return deferred.promise();
};

jigna.AsyncClient.prototype.call_instance_method = function(id, method_name, args) {
    /* Calls an instance method. Do not use this to call any long running
    methods.

    Note: Since this is an async client, it won't block the UI even if you
    call a long running method here but the UI updates (progress bars etc)
    won't be available until the server completes running that method.
    */
    var request = {
        kind        : 'call_instance_method',
        id          : id,
        method_name : method_name,
        args        : this._marshal_all(args)
    };
    var client = this;

    var deferred = new $.Deferred();
    this.send_request(request).done(function(response){
        deferred.resolve(client._unmarshal(response));
    });

    return deferred.promise();
};

jigna.AsyncClient.prototype.call_instance_method_thread = function(id, method_name, args) {
    /* Calls an instance method in a thread on the server. Use this to call
    any long running method on the server otherwise you won't get any UI
    updates on the client.
    */
    var request = {
        kind        : 'call_instance_method_thread',
        id          : id,
        method_name : method_name,
        args        : this._marshal_all(args),
    };
    var client = this;

    // Note that this deferred is resolved when the method called in a thread
    // finishes, not when the request to call the method finishes.
    // This is done to make this similar to the sync client so that the users
    // can attach their handlers when the method is done.
    var deferred = new $.Deferred();

    this.send_request(request).done(function(response){

        var future_obj = client._unmarshal(response);
        // the response of a threaded request is a marshalled version of a python
        // future object. We attach 'done' and 'error' handlers on that object to
        // resolve/reject our own deferred.

        jigna.add_listener(future_obj, 'done', function(event){
            deferred.resolve(event.data);
        });

        jigna.add_listener(future_obj, 'error', function(event){
            deferred.reject(event.data);
        });

    });

    return deferred.promise();
};

jigna.AsyncClient.prototype.get_attribute = function(proxy, attribute) {
    /* Get the specified attribute of the proxy from the server. */
    var client = this;

    // start a new request only if a request for getting that attribute isn't
    // already sent
    if (proxy.__state__[attribute] != 'busy') {
        proxy.__state__[attribute] = 'busy';

        var request = this._create_request(proxy, attribute);
        this.send_request(request).done(function(response){
            // update the proxy cache
            proxy.__cache__[attribute] = client._unmarshal(response);

            // fire the object changed event to trigger fresh fetches from
            // the cache
            jigna.fire_event('jigna', {name: 'object_changed', object: proxy});

            // set the state as free again so that further fetches ask the
            // server again
            proxy.__state__[attribute] = undefined;

        });
    }

    var result;
    var info = proxy.__info__;
    if (info && (info.attribute_values !== undefined)) {
        // This is an object.
        var index = info.attribute_names.indexOf(attribute);
        result = info.attribute_values[index];
    } else {
        // this is a dict/list.
        result = proxy.__cache__[attribute];
    }
    return result;
};
