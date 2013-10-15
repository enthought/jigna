$(document).ready(function(){
    window.jigna = {

        scope: $(document.body).scope(),

        bridge: window["python"],

        id_to_model_map: {},

        add_model: function(id, model_name, traits) {
            /* Add the model named `model_name` to jigna models. Expose the
            ** list of traits to jigna.
            */
            var model = this.make_model(id, traits);

            this.id_to_model_map[id] = model;

            this._add_in_scope(model_name, model)
        },

        make_model: function(id, traits) {
            /* Add the model named `model_name` to jigna models. Expose the
             * list of traits to jigna.
            */
            var model = new jigna.JignaModel(id);

            for (var index in traits) {
                this._add_property_to_model(id, model, traits[index]);
            }

            return model;
        },

        on_trait_change: function(id, trait_name, value) {
            this.scope.$apply(function(){})
        },

        /***************** Private protocol ********************************/

        _add_property_to_model: function(id, model, trait) {
            var descriptor = this._make_descriptor(id, trait);
            Object.defineProperty(model, trait, descriptor);
        },

        _add_in_scope: function(model_name, model) {
            this.scope.$apply(
                function() {
                    jigna.scope[model_name] = model;
                }
            )
        },

        _make_descriptor: function(id, trait) {
            var get = function() {
                return JSON.parse(
                    jigna.bridge.get_trait(id, trait)
                );
            };

            var set = function(value) {
                jigna.bridge.set_trait(
                    id,
                    trait,
                    JSON.stringify(value)
                );
            };

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
