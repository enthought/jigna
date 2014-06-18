///////////////////////////////////////////////////////////////////////////////
// QtBridge (intra-process)
///////////////////////////////////////////////////////////////////////////////

jigna.QtBridge = function(client, qt_bridge) {
    this.ready = new $.Deferred();

    // Private protocol
    this._client    = client;
    this._qt_bridge = qt_bridge;

    this.ready.resolve();
};

jigna.QtBridge.prototype.handle_event = function(jsonized_event) {
    /* Handle an event from the server. */
    this._client.handle_event(jsonized_event);
};

jigna.QtBridge.prototype.send_request = function(jsonized_request) {
    /* Send a request to the server and wait for the reply. */

    result = this._qt_bridge.handle_request(jsonized_request);

    return result;
};

jigna.QtBridge.prototype.send_request_async = function(jsonized_request) {
    /* A dummy async version of the send_request method. Since QtBridge is
    single process, this method indeed waits for the reply but presents
    a deferred API so that the AsyncClient can use it. Mainly for testing
    purposes only. */

    var deferred = new $.Deferred();

    deferred.resolve(this._qt_bridge.handle_request(jsonized_request));

    return deferred.promise();
};
