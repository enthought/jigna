$(document).ready(function(){
    window.jigna = {

        scope: $(document.body).scope(),

        bridge: window["python"],

        _make_getter: function(model_name, trait) {
            return function() {
                return JSON.parse(
                    jigna.bridge.get_trait(model_name, trait)
                );
            };
        },

        _make_setter: function(model_name, trait, value) {
            return function(value) {
                jigna.bridge.set_trait(
                    model_name,
                    trait,
                    JSON.stringify(value)
                );
            };
        },

        add_model: function(model_name, traits) {
            /* Add the model named `model_name` to jigna models. Expose the list of
            * traits to jigna.
            */
            var model = new jigna.JignaModel2(model_name);

            for (var index in traits) {
                var trait = traits[index];

                var descriptor = {
                    enumerable: true,
                    writeable: true,
                    get: this._make_getter(model_name, trait),
                    set: this._make_setter(model_name, trait)
                };

                Object.defineProperty(model, trait, descriptor);
            }

            // Add the model to the scope
            this._add_in_scope(model_name, model)

            return
        },

        /**** Private API ********************************************************************/

        _add_in_scope: function(model_name, model) {
            this.scope.$apply(function(){
                jigna.scope[model_name] = model;
            })
        }

    }

    /**** JignaModel *************************************************************************/

    jigna.JignaModel = function(model_name) {
        this.model_name = model_name;
    };

    jigna.JignaModel.prototype.setup_js_watcher = function(trait_name) {
        /* Sets up the watcher for communicating change in trait `trait_name` in JS world to
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

    jigna.JignaModel.prototype.set_trait_in_js = function(trait_name, value) {
        /* Sets the trait in js.
        */
        var model = this;
        setTimeout(function(){
            model._set_in_scope(trait_name, value)
        }, 0)
    };

    /**** Private protocol ******************************************************************/

    jigna.JignaModel.prototype._set_in_scope = function(trait_name, value) {
        var model = this;
        jigna.scope.$apply(function(){
            model[trait_name] = value;
        })
    }

    /**** JignaModel2 ****************************************************/

    jigna.JignaModel2 = function(model_name) {
        this.model_name = model_name;
    };


})
