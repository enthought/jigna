// An AngularJS app running the jigna app

define(['jquery', 'angular', 'jigna'], function($, angular, jigna){

    var jigna_app = angular.module('jigna', []);

    // Add initialization function on module run time
    jigna_app.run(['$rootScope', '$compile', function($rootScope, $compile){

        // add the 'jigna' namespace to the $rootScope. This is done so that
        // any special jigna methods are easily available in directives like
        // ng-click, ng-mouseover etc.
        $rootScope.jigna = jigna;

        var add_to_scope = function(models){
            for (var model_name in models) {
                $rootScope[model_name] = models[model_name];
            }

            jigna.fire_event(jigna, 'object_changed');
        };

        // add the existing models to the angular scope
        add_to_scope(jigna.models);

        // Whenever a new model is added to jigna, add it to the angular
        // scope as well
        jigna.add_listener('jigna', 'model_added', function(event){
            add_to_scope(event.data);
        });

        // Start the $digest cycle on rootScope whenever anything in the
        // model object is changed.
        //
        // Since the $digest cycle essentially involves dirty checking of
        // all the watchers, this operation means that it will trigger off
        // new GET requests for each model attribute that is being used in
        // the registered watchers.
        jigna.add_listener(jigna, 'object_changed', function() {
            if ($rootScope.$$phase === null){
                $rootScope.$digest();
            }
        });

    }]);

    return jigna_app;
});
