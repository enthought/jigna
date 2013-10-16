$(document).ready(function(){
    window.jigna = {

        /***************** Public protocol ********************************/

        scope: $(document.body).scope(),

        add_model: function(id, model_name, trait_info) {
            /* Add the model named `model_name` to jigna models. Expose the
            ** list of traits to jigna.
            */
            var model = this._make_model(id, trait_info);

            this._id_to_model_map[id] = model;

            this._add_in_scope(model_name, model)
        },

        on_trait_change: function(id, trait_name, value) {
            this.scope.$apply(
                function() {
                    jigna._id_to_model_map[id][trait_name] = value;
                }
            );
        },

        /***************** Private protocol ********************************/

        _bridge: window["python_bridge"],

        _id_to_model_map: {},

        _add_in_scope: function(model_name, model) {
            this.scope.$apply(
                function() {
                    jigna.scope[model_name] = model;
                }
            )
        },

        _add_property_to_model: function(id, model, trait_name, trait_info) {
            var descriptor = this._make_descriptor(id, trait_name, trait_info);
            Object.defineProperty(model, trait_name, descriptor);
        },

        _make_descriptor: function(id, trait_name, trait_info) {
            var factories = {
                "instance": this._make_instance_descriptor,
                "primitive": this._make_primitive_descriptor,
            };
            var factory = factories[trait_info["type"]];

            return factory(id, trait_name, trait_info);
        },

        _make_instance_descriptor: function(id, trait_name, trait_info) {
            var get = function() {
                var id = trait_info["id"];
                var model = jigna._id_to_model_map[id];
                if (model === undefined) {
                    var model_info = JSON.parse(
                        jigna._bridge.get_trait_info(id)
                    );
                    model = jigna._make_model(id, model_info);
                    jigna._id_to_model_map[id] = model;
                }
                return model;
            };

            var set = function(new_id) {
                var info = {type: "instance", id: String(new_id)};
                var descriptor = jigna._make_descriptor(id, trait_name, info);
                Object.defineProperty(this, trait_name, descriptor);
            };

            return {
                enumerable: true,
                writeable: true,
                configurable: true,
                get: get,
                set: set
            };
        },

        _make_model: function(id, trait_info) {
            /* Add the model named `model_name` to jigna models. Expose the
             * list of traits to jigna.
            */
            var model = new jigna.JignaModel(id);

            for (var trait_name in trait_info) {
                this._add_property_to_model(
                    id, model, trait_name, trait_info[trait_name]
                );
            }

            return model;
        },

        _make_primitive_descriptor: function(id, trait_name, trait_info) {
            var get = function() {
                return JSON.parse(
                    jigna._bridge.get_trait(id, trait_name)
                );
            };

            var set = function(value) {
                jigna._bridge.set_trait(
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
        },

    }

    /**** JignaModel ******************************************************/

    jigna.JignaModel = function(id) {
        this.__id = id;
    };

})
