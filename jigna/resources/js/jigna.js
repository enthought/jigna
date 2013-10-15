$(document).ready(function(){
    window.jigna = {

        scope: $(document.body).scope(),

        bridge: window["python"],

        id_to_model_map: {},

        add_model: function(id, model_name, trait_info) {
            /* Add the model named `model_name` to jigna models. Expose the
            ** list of traits to jigna.
            */
            var model = this.make_model(id, trait_info);

            this.id_to_model_map[id] = model;

            this._add_in_scope(model_name, model)
        },

        make_model: function(id, trait_info) {
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

        on_trait_change: function(id, trait_name, value) {
            this.scope.$apply(function(){})
        },

        /***************** Private protocol ********************************/

        _add_property_to_model: function(id, model, trait_name, trait_info) {
            var descriptor = this._make_descriptor(id, trait_name, trait_info);
            Object.defineProperty(model, trait_name, descriptor);
        },

        _add_in_scope: function(model_name, model) {
            this.scope.$apply(
                function() {
                    jigna.scope[model_name] = model;
                }
            )
        },

        _make_descriptor: function(id, trait_name, trait_info) {
            var get_primitive = function() {
                return JSON.parse(
                    jigna.bridge.get_trait(id, trait_name)
                );
            };

            var set_primitive = function(value) {
                jigna.bridge.set_trait(
                    id,
                    trait_name,
                    JSON.stringify(value)
                );
            };

            var get_instance = function() {
                var id = trait_info["id"];
                var model = jigna.id_to_model_map[id];
                if (model === undefined) {
                    var model_info = JSON.parse(
                        jigna.bridge.get_trait_info(id)
                    );
                    model = jigna.make_model(id, model_info);
                    jigna.id_to_model_map[id] = model;
                }
                return model;
            };

            var get, set;
            if (trait_info["type"] === "primitive") {
                get = get_primitive;
                set = set_primitive;
            }
            else {
                get = get_instance;
                set = undefined;
            }
            return {
                enumerable: true,
                writeable: true,
                get: get,
                set: set
            };
        }
    }

    /**** JignaModel ******************************************************/

    jigna.JignaModel = function(id) {
        this.__id = id;
    };

})

//
//    jigna.JignaModel.prototype.setup_js_watcher = function(trait_name) {
//        /* Sets up the watcher for communicating change in trait `trait_name` i
//n JS world to
//        Python world.
//        */
//        var model = this;
//        var watch_expr = model.__model_name + '.' + trait_name;
//        jigna.scope.$watch(watch_expr, function(value){
//            model.set_trait_in_python(trait_name, value);
//        })
//
//        return
//    };
//
//    jigna.JignaModel.prototype.set_trait_in_python = function(trait_name, value) {
//        /* Sets the trait in python.
//        */
//        var model = this;
//        if (!(value === undefined)) {
//            jigna.bridge.set_trait(model.__model_name, trait_name, JSON.stringify(value));
//        }
//    };
//
//
