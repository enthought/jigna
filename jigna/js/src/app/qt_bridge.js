///////////////////////////////////////////////////////////////////////////////
// QtBridge (intra-process)
///////////////////////////////////////////////////////////////////////////////

define(['jquery'], function($){

	QtBridge = function(client, qt_bridge) {
        this.ready = new $.Deferred();

        // Private protocol
        this._client    = client;
        this._qt_bridge = qt_bridge;

        this.ready.resolve();
    };

    QtBridge.prototype.handle_event = function(jsonized_event) {
        /* Handle an event from the server. */
        this._client.handle_event(jsonized_event);
    };

    QtBridge.prototype.send_request = function(jsonized_request) {
        /* Send a request to the server and wait for the reply. */

        result = this._qt_bridge.handle_request(jsonized_request);

        return result;
    };

    return QtBridge;
});
