$(document).ready(function(){
    window.jigna = {

        scope: $(document.body).scope(),

        py_obj: window["python"],

        add_model: function(model_name, traits) {
            /* Add the model named `model_name` to jigna models. Expose the list of
            * traits to jigna.
            */
            var self = this;

            var model = new jigna.JignaModel(model_name, traits);

            // Add the model to the scope
            self._add_in_scope(model_name, model)

            return
        },

        /**** Private API ********************************************************************/

        _add_in_scope: function(model_name, model) {
            var self = this;
            self.scope.$apply(function(){
                self.scope[model_name] = model;
            })
        }

    }

    /**** JignaModel *************************************************************************/

    jigna.JignaModel = function(model_name, traits) {
        var self = this;
        self.model_name = model_name;
    };

    jigna.JignaModel.prototype.setup_js_watcher = function(trait_name) {
        /* Sets up the watcher for communicating change in trait `trait_name` in JS world to 
        Python world.
        */
        var self = this;
        var watch_expr = self.model_name + '.' + trait_name;
        jigna.scope.$watch(watch_expr, function(value){
            self.set_trait_in_python(trait_name, value);
        })

        return
    };

    jigna.JignaModel.prototype.set_trait_in_python = function(trait_name, value) {
        /* Sets the trait in python.
        */
        var self = this;
        if (!(value === undefined)) {
            jigna.py_obj.set_trait(self.model_name, trait_name, JSON.stringify(value));
        }
    };

    jigna.JignaModel.prototype.set_trait_in_js = function(trait_name, value) {
        /* Sets the trait in js.
        */
        var self = this;
        setTimeout(function(){
            self._set_in_scope(trait_name, value)
        }, 0)
    };

    /**** Private protocol ******************************************************************/

    jigna.JignaModel.prototype._set_in_scope = function(trait_name, value) {
        var self = this;
        jigna.scope.$apply(function(){
            self[trait_name] = value;
        })
    }

})