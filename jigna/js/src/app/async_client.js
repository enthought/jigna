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

    return proxy.__cache__[attribute];
};

jigna.AsyncClient.prototype.on_object_changed = function(event){
    if (jigna.debug) {
        this.print_JS_message('------------on_object_changed--------------');
        this.print_JS_message('object id  : ' + event.obj);
        this.print_JS_message('attribute  : ' + event.name);
        this.print_JS_message('items event: ' + event.items_event);
        this.print_JS_message('new type   : ' + event.data.type);
        this.print_JS_message('new value  : ' + event.data.value);
        this.print_JS_message('new info   : ' + event.data.info);
        this.print_JS_message('-------------------------------------------');
    }

    var proxy = this._id_to_proxy_map[event.obj];

    // If the *contents* of a list/dict have changed then we need to update
    // the associated proxy to reflect the change.
    if (event.items_event) {
        var collection_proxy = this._id_to_proxy_map[event.data.value];
        // The collection proxy can be undefined if on the Python side you
        // have re-initialized a list/dict with the same value that it
        // previously had, e.g.
        //
        // class Person(HasTraits):
        //     friends = List([1, 2, 3])
        //
        // fred = Person()
        // fred.friends = [1, 2, 3] # No trait changed event!!
        //
        // This is because even though traits does copy on assignment for
        // lists/dicts (and hence the new list will have a new Id), it fires
        // the trait change events only if it considers the old and new values
        // to be different (ie. if does not compare the identity of the lists).
        //
        // For us(!), it means that we won't have seen the new list before we
        // get an items changed event on it.
        if (collection_proxy === undefined) {
            // In the async case, we do not create a new proxy instead we
            // update the id_to_proxy map and update the proxy with the
            // dict/list event info.
            collection_proxy = proxy.__cache__[event.name];
            this._id_to_proxy_map[event.data.value] = collection_proxy;
        }
        this._proxy_factory.update_proxy(
            collection_proxy, event.data.type, event.data.info
        );

    } else {
        proxy.__cache__[event.name] = this._unmarshal(event.data);
    }

    // Angular listens to this event and forces a digest cycle which is how it
    // detects changes in its watchers.
    jigna.fire_event('jigna', {name: 'object_changed', object: proxy});
};

// Private protocol //////////////////////////////////////////////////////////

jigna.AsyncClient.prototype._create_proxy_factory = function() {
    return new jigna.AsyncProxyFactory(this);
};
