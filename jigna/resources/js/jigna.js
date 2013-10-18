var jigna = {};

jigna.Controller = function(scope){

    this.scope = scope;

    this._bridge = window["python_bridge"];

    this._id_to_model_map = {};

}

jigna.Controller.prototype.add_model = function(id, model_name, trait_info) {
    /* Add the model named `model_name` to jigna models. Expose the
    ** list of traits to jigna.
    */
    var proxy = this._make_proxy(id, trait_info);

    this._id_to_model_map[id] = proxy;

    this._add_in_scope(model_name, proxy)
};

jigna.Controller.prototype.on_list_items_change = function(id, trait_name, value) {
    this.scope.$apply(
        function() {
            //var list = jigna._id_to_model_map[id][trait_name];
            //list.splice.apply(list, value);
        }
    );
};

jigna.Controller.prototype.on_trait_change = function(id, trait_name, value) {
    console.log("this, scope:", this, this.scope);
    this.scope.$apply(
        function() {
            jigna.controller._id_to_model_map[id][trait_name] = value;
        }
    );
};

/***************** Private protocol ********************************/

jigna.Controller.prototype._add_in_scope = function(model_name, proxy) {
    this.scope.$apply(
        function() {
            jigna.controller.scope[model_name] = proxy;
        }
    )
};

jigna.Controller.prototype._add_property_to_proxy = function(id, proxy, trait_name, trait_info) {
    var descriptor = this._make_descriptor(id, trait_name, trait_info);
    Object.defineProperty(proxy, trait_name, descriptor);
};

jigna.Controller.prototype._get_model_from_id = function(id) {
    var model = this._id_to_model_map[id];
    if (model === undefined) {
        var model_info = JSON.parse(
            this._bridge.get_trait_info(id)
        );
        model = this._make_proxy(id, model_info);
        this._id_to_model_map[id] = model;
    }
    return model;
};

jigna.Controller.prototype._make_descriptor = function(id, trait_name, trait_info) {
    var factories = {
        "instance": this._make_instance_descriptor,
        "primitive": this._make_primitive_descriptor,
        "list_instance": this._make_list_instance_descriptor,
        "list_primitive": this._make_primitive_descriptor
    };
    var factory = factories[trait_info["type"]];

    return factory(id, trait_name);
};

jigna.Controller.prototype._make_instance_descriptor = function(id, trait_name) {
    var get = function() {
        var id = trait_info["id"];
        return jigna.controller._get_model_from_id(id);
    };

    var set = function(new_id) {
        var info = {type: "instance", id: String(new_id)};
        var descriptor = jigna.controller._make_descriptor(id, trait_name, info);
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

jigna.Controller.prototype._make_list_instance_descriptor = function(id, trait_name) {
    var get = function() {
        var result = [];
        var list_info = JSON.parse(
            jigna.controller._bridge.get_trait(id, trait_name)
        );
        for (var index in list_info) {
            result.push(jigna.controller._get_model_from_id(list_info[index]));
        }
        return result;
    };

    var set = function(new_ids) {
        var info = {type: "list_instance",
                    value: JSON.stringify(new_ids)};
        var descriptor = jigna.controller._make_descriptor(id, trait_name, info);
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

jigna.Controller.prototype._make_proxy = function(id, trait_info) {
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

jigna.Controller.prototype._make_primitive_descriptor = function(id, trait_name) {
    var get = function() {
        return JSON.parse(
            jigna.controller._bridge.get_trait(id, trait_name)
        );
    };

    var set = function(value) {
        jigna.controller._bridge.set_trait(
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
}

jigna.InstanceProxy = function(id) {
    this.__id = id;
};

jigna.ListProxy = function(id) {
    this.__id = id;
};



$(document).ready(function(){
    var scope = $(document.body).scope();
    jigna.controller = new jigna.Controller(scope);
})