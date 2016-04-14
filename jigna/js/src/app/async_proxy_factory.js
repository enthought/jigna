/////////////////////////////////////////////////////////////////////////////
// AsyncProxyFactory
/////////////////////////////////////////////////////////////////////////////

jigna._SavedData = function(data) {
    // Used internally to save marshaled data to unmarshal later.
    this.data = data;
};

jigna.AsyncProxyFactory = function(client) {
    jigna.ProxyFactory.call(this, client);
};

jigna.AsyncProxyFactory.prototype = Object.create(
    jigna.ProxyFactory.prototype
);

jigna.AsyncProxyFactory.prototype.constructor = jigna.AsyncProxyFactory

jigna.AsyncProxyFactory.prototype._add_instance_attribute = function(proxy, attribute_name){
    var descriptor, get, set;

    get = function() {
        // In here, 'this' refers to the proxy!
        var value = this.__cache__[attribute_name];
        if (value === undefined) {
            value = this.__client__.get_attribute(this, attribute_name);
            if (value === undefined) {
                var info = this.__info__;
                if (info && (info.attribute_values !== undefined)) {
                    var index = info.attribute_names.indexOf(attribute_name);
                    value = this.__client__._unmarshal(
                        info.attribute_values[index]
                    );
                }
            } else {
                this.__cache__[attribute_name] = value;
            }
        }

        return value;
    };

    set = function(value) {
        // In here, 'this' refers to the proxy!
        //
        // If the proxy is for a 'HasTraits' instance then we don't need
        // to set the cached value here as the value will get updated when
        // we get the corresponding trait event. However, setting the value
        // here means that we can create jigna UIs for non-traits objects - it
        // just means we won't react to external changes to the model(s).
        this.__cache__[attribute_name] = value;
        this.__client__.set_instance_attribute(
            this.__id__, attribute_name, value
        );
    };

    descriptor = {enumerable:true, get:get, set:set, configurable:true};
    Object.defineProperty(proxy, attribute_name, descriptor);
};

jigna.AsyncProxyFactory.prototype._populate_dict_proxy = function(proxy, info) {
    var index, key;
    var values = info.values;

    for (index=0; index < info.keys.length; index++) {
        key = info.keys[index];
        this._add_item_attribute(proxy, key);
        proxy.__cache__[key] = new jigna._SavedData(values.data[index]);
    }
};

jigna.AsyncProxyFactory.prototype._update_dict_proxy = function(proxy, info) {
    var removed = info.removed;
    var cache = proxy.__cache__;
    var key;

    // Add the keys in the added.
    this._populate_dict_proxy(proxy, info.added);

    for (var index=0; index < removed.length; index++) {
        key = removed[index];
        delete cache[key];
        delete proxy[key];
    }
};

jigna.AsyncProxyFactory.prototype._populate_list_proxy = function(proxy, info) {
    /* Populate the items in a list proxy. */

    var data = info.data;
    for (var index=0; index < info.length; index++) {
        this._add_item_attribute(proxy, index);
        proxy.__cache__[index] = new jigna._SavedData(data[index]);
    }

    return proxy;
};

jigna.AsyncProxyFactory.prototype._update_list_proxy = function(proxy, info) {
    /* Update the given proxy. */

    if (info.index === undefined) {
        // This is an extended slice.  Note that one cannot increase the size
        // of the list with an extended slice.  So one is either deleting
        // elements or changing them.
        var index;
        var added = info.added;
        var removed = info.removed - added.length;
        var cache = proxy.__cache__;
        var end = cache.length;
        if (removed > 0) {
            // Delete the proxy indices at the end.
            for (index=end; index > (end-removed) ; index--) {
                delete proxy[index-1];
            }
            var to_remove = [];
            for (index=info.start; index<info.stop; index+=info.step) {
                to_remove.push(index);
            }
            // Delete the cached entries in sequence from the back.
            for (index=to_remove.length; index > 0; index--) {
                cache.splice(to_remove[index-1], 1);
            }
        } else {
            // When nothing is removed, just update the cache entries.
            for (var i=0; i < added.length; i++) {
                index = info.start + i*info.step;
                cache[index] = new jigna._SavedData(added.data[i]);
            }
        }
    } else {
        // This is not an extended slice.
        var splice_args = [info.index, info.removed].concat(
            info.added.data.map(function(x) {return new jigna._SavedData(x);})
        );

        var extra = splice_args.length - 2 - splice_args[1];
        var cache = proxy.__cache__;
        var end = cache.length;
        if (extra < 0) {
            for (var index=end; index > (end+extra) ; index--) {
                delete proxy[index-1];
            }
        } else {
            for (var index=0; index < extra; index++){
                this._add_item_attribute(proxy, end+index);
            }
        }
        cache.splice.apply(cache, splice_args);
    }
};


// Common for list and dict proxies ////////////////////////////////////////////

jigna.AsyncProxyFactory.prototype._add_item_attribute = function(proxy, index){
    var descriptor, get, set;

    get = function() {
        // In here, 'this' refers to the proxy!
        var value = this.__cache__[index];
        if (value === undefined) {
            value = this.__client__.get_attribute(this, index);
            this.__cache__[index] = value;
        } else if (value instanceof jigna._SavedData) {
            value = this.__client__._unmarshal(value.data);
            this.__cache__[index] = value;
        }

        return value;
    };

    set = function(value) {
        // In here, 'this' refers to the proxy!
        this.__cache__[index] = value;
        this.__client__.set_item(this.__id__, index, value);
    };

    descriptor = {enumerable:true, get:get, set:set, configurable:true};
    Object.defineProperty(proxy, index, descriptor);
};
