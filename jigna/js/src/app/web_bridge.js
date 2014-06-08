///////////////////////////////////////////////////////////////////////////////
// WebBridge
///////////////////////////////////////////////////////////////////////////////

define(['jquery'], function($){

	WebBridge = function(client) {
        this._client = client;

        // The jigna_server attribute can be set by a client to point to a
        // different Jigna server.
        var jigna_server = window['jigna_server'];
        if (jigna_server === undefined) {
            jigna_server = window.location.host;
        }
        this._server_url = 'http://' + jigna_server;

        var url = 'ws://' + jigna_server + '/_jigna_ws';

        this._deferred_requests = {};
        this._request_ids = [];
        for (var index=0; index < 1024; index++) {
            this._request_ids.push(index);
        }

        this._web_socket = new WebSocket(url);
        this._ws_opened = new $.Deferred();
        var bridge = this;
        this._web_socket.onopen = function() {
            bridge._ws_opened.resolve();
        }
        console.log("specifying _web_socket:", this._web_socket);
        this._web_socket.onmessage = function(event) {
            console.log("handle event:", event);
            bridge.handle_event(event.data);
        };
    };

    WebBridge.prototype.handle_event = function(jsonized_event) {
        /* Handle an event from the server. */
        var response = JSON.parse(jsonized_event);
        console.log("handling event....", response);
        var request_id = response[0];
        var jsonized_response = response[1];
        if (request_id === -1) {
        	console.log("handling it in sync fashion");
            this._client.handle_event(jsonized_response);
        }
        else {
            var deferred = this._pop_deferred_request(request_id);
            deferred.resolve(jsonized_response);
        }
    };

    WebBridge.prototype._pop_deferred_request = function(request_id) {
        var deferred = this._deferred_requests[request_id];
        delete this._deferred_requests[request_id];
        this._request_ids[request_id] = request_id;
        return deferred;
    };

    WebBridge.prototype._push_deferred_request = function(deferred) {
        var id = this._request_ids.pop();
        this._deferred_requests[id] = deferred;
        return id;
    };

    WebBridge.prototype.send_request = function(jsonized_request) {
        if (jigna.async) {
            return this._send_request_async(jsonized_request);
        }
        else {
            return this._send_request_sync(jsonized_request);
        }
    };

    WebBridge.prototype._send_request_async = function(jsonized_request) {
        /* Send a request to the server and do not wait and return a Promise
           which is resolved upon completion of the request.
        */

        var deferred = new $.Deferred();
        var request_id = this._push_deferred_request(deferred);
        var bridge = this;
        this._ws_opened.done(function() {
            bridge._web_socket.send(JSON.stringify([request_id, jsonized_request]));
        });
        return deferred.promise();
    };

    WebBridge.prototype._send_request_sync = function(jsonized_request) {
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

    return WebBridge;
})
