// An AngularJS app running the jigna app

define(['jquery', 'angular', 'jigna'], function($, angular, jigna){

    var jigna_app = angular.module('jigna', []);

    // Add initialization function on module run time
    jigna_app.run(['$rootScope', '$compile', function($rootScope, $compile){

        // Add all jigna models as scope variables
        var add_to_scope = function(context) {
            for (var model_name in context) {
                $rootScope[model_name] = jigna.models[model_name];
            }
            jigna.fire_event(jigna, 'object_changed');
        };

        // Listen to context change event in jigna. A context change event is
        // fired whenever new toplevel models are added to the jigna scope.
        jigna.add_listener('jigna', 'context_updated', function(event){
            add_to_scope(event.data);
        });

        // Listen to object change events in jigna
        jigna.add_listener(jigna, 'object_changed', function() {
            if ($rootScope.$$phase === null){
                $rootScope.$digest();
            }
        });

        // Create a fake event so that initial context is updated on scope
        //jigna.fire_event(jigna, 'context_updated', jigna.models);
        add_to_scope(jigna.models);

    }]);

    return jigna_app;
});
