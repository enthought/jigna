var jigna = {};

jigna.ProxyManager = function(scope){

    this.scope = scope;

    this._bridge = window["python_bridge"];

    this._id_to_proxy_map = {};

    this._proxy_factory = new jigna.ProxyFactory(this);

}

jigna.ProxyManager.prototype.add_model = function(id, model_name, trait_info) {
    /* Add the model named `model_name` to jigna models. Expose the
    ** list of traits to jigna.
    */
    var proxy = this._proxy_factory.make_proxy(id, trait_info);

    this._id_to_proxy_map[id] = proxy;

    this._add_in_scope(model_name, proxy)
};

jigna.ProxyManager.prototype.on_list_items_change = function(id, trait_name, value) {
    this.scope.$apply(
        function() {
            //var list = jigna._id_to_proxy_map[id][trait_name];
            //list.splice.apply(list, value);
        }
    );
};

jigna.ProxyManager.prototype.on_trait_change = function(id, trait_name, value) {
    console.log("this, scope:", this, this.scope);
    this.scope.$apply(
        function() {
            jigna.proxy_manager._id_to_proxy_map[id][trait_name] = value;
        }
    );
};

/***************** Private protocol ********************************/

jigna.ProxyManager.prototype._add_in_scope = function(model_name, proxy) {
    this.scope.$apply(
        function() {
            jigna.proxy_manager.scope[model_name] = proxy;
        }
    )
};

jigna.ProxyManager.prototype._get_proxy_from_id = function(id) {
    var proxy = this._id_to_proxy_map[id];
    if (proxy === undefined) {
        var trait_info = JSON.parse(
            this._bridge.get_trait_info(id)
        );
        proxy = this._proxy_factory.make_proxy(id, trait_info);
        this._id_to_proxy_map[id] = proxy;
    }
    return proxy;
};

// ProxyFactory object

jigna.ProxyFactory = function(proxy_manager) {
    this.proxy_manager = proxy_manager;
};

jigna.ProxyFactory.prototype.make_proxy = function(id, trait_info) {
    /* Add the model named `model_name` to jigna models. Expose the
     * list of traits to jigna.
    */
    var proxy = new jigna.InstanceProxy(id);

    for (var trait_name in trait_info) {
        this._add_property_to_proxy(
            id, proxy, trait_name, trait_info[trait_name]
        );
    }

    return proxy;
};

jigna.ProxyFactory.prototype._add_property_to_proxy = function(id, proxy, trait_name, trait_info) {
    var descriptor = this._make_descriptor(id, trait_name, trait_info);
    Object.defineProperty(proxy, trait_name, descriptor);
};

jigna.ProxyFactory.prototype._make_descriptor = function(id, trait_name, trait_info) {
    var factories = {
        "instance": this._make_instance_descriptor,
        "primitive": this._make_primitive_descriptor,
        "list_instance": this._make_list_instance_descriptor,
        "list_primitive": this._make_primitive_descriptor
    };
    var factory = factories[trait_info["type"]];

    return factory(id, trait_name);
};

jigna.ProxyFactory.prototype._make_instance_descriptor = function(id, trait_name) {
    var proxy_factory = this;
    var get = function() {
        return jigna.proxy_manager._get_proxy_from_id(trait_info["id"]);
    };

    var set = function(new_id) {
        var info = {type: "instance", id: String(new_id)};
        var descriptor = proxy_factory._make_descriptor(id, trait_name, info);
        Object.defineProperty(this, trait_name, descriptor);
    };

    return {
        enumerable: true,
        writeable: true,
        configurable: true,
        get: get,
        set: set
    };
};

jigna.ProxyFactory.prototype._make_list_instance_descriptor = function(id, trait_name) {
    var proxy_factory = this;
    var get = function() {
        var result = [];
        var list_info = JSON.parse(
            jigna.proxy_manager._bridge.get_trait(id, trait_name)
        );
        for (var index in list_info) {
            result.push(jigna.proxy_manager._get_proxy_from_id(list_info[index]));
        }
        return result;
    };

    var set = function(new_ids) {
        var info = {type: "list_instance",
                    value: JSON.stringify(new_ids)};
        var descriptor = proxy_factory._make_descriptor(id, trait_name, info);
        Object.defineProperty(this, trait_name, descriptor);
    };

    return {
        enumerable: true,
        writeable: true,
        configurable: true,
        get: get,
        set: set
    };
};

jigna.ProxyFactory.prototype._make_primitive_descriptor = function(id, trait_name) {
    var get = function() {
        return JSON.parse(
            jigna.proxy_manager._bridge.get_trait(id, trait_name)
        );
    };

    var set = function(value) {
        jigna.proxy_manager._bridge.set_trait(
            id,
            trait_name,
            JSON.stringify(value)
        );
    };

    return {
        enumerable: true,
        writeable: true,
        configurable: true,
        get: get,
        set: set
    };
};

jigna.InstanceProxy = function(id) {
    this.__id = id;
};

jigna.ListProxy = function(id) {
    this.__id = id;
};



$(document).ready(function(){
    var scope = $(document.body).scope();
    jigna.proxy_manager = new jigna.ProxyManager(scope);
})