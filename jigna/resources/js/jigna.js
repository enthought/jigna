$(document).ready(function(){
    window.jigna = {

        scope: $(document.body).scope(),

        bridge: window["python"],

        add_model: function(model_name, traits) {
            /* Add the model named `model_name` to jigna models. Expose the list of
            * traits to jigna.
            */
            var model = new jigna.JignaModel(model_name);

            for (var index in traits) {
                this._add_property_to_model(model, model_name, traits[index]);
            }

            this._add_in_scope(model_name, model)
        },

        /***************** Private protocol ********************************/

        _add_property_to_model: function(model, model_name, trait) {
            var descriptor = this._make_descriptor(model_name, trait);
            Object.defineProperty(model, trait, descriptor);
        },

        _add_in_scope: function(model_name, model) {
            this.scope.$apply(
                function() {
                    jigna.scope[model_name] = model;
                }
            )
        },

        _make_descriptor: function(model_name, trait) {
            var get = function() {
                return JSON.parse(
                    jigna.bridge.get_trait(model_name, trait)
                );
            };

            var set = function(value) {
                jigna.bridge.set_trait(
                    model_name,
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


    jigna.JignaModel = function(model_name) {
        this.model_name = model_name;
    };

    jigna.JignaModel.prototype.set_trait_in_js = function(trait_name, value) {
        var model = this;
        setTimeout(function(){
            model._set_in_scope(trait_name, value)
        }, 0)
    };

    jigna.JignaModel.prototype.setup_js_watcher = function(trait_name) {
        /* Sets up the watcher for communicating change in trait `trait_name` i
n JS world to
        Python world.
        */
        var model = this;
        var watch_expr = model.model_name + '.' + trait_name;
        jigna.scope.$watch(watch_expr, function(value){
            model.set_trait_in_python(trait_name, value);
        })

        return
    };

    jigna.JignaModel.prototype.set_trait_in_python = function(trait_name, value) {
        /* Sets the trait in python.
        */
        var model = this;
        if (!(value === undefined)) {
            jigna.bridge.set_trait(model.model_name, trait_name, JSON.stringify(value));
        }
    };

    /**** Private protocol ************************************************/

    jigna.JignaModel.prototype._set_in_scope = function(trait_name, value) {
        var model = this;
        jigna.scope.$apply(function(){})
    }

})
