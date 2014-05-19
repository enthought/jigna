// An AngularJS app running the jigna app

define(['jquery', 'angular', 'jigna'], function($, angular, jigna){

    var module = angular.module('jigna', []);

    // Add initialization function on module run time
    module.run(['$rootScope', '$compile', function($rootScope, $compile){

        // First initialize jigna
        jigna.initialize();

        // Add all jigna models as scope variables
        var add_to_scope = function(context) {
            for (var model_name in context) {
                $rootScope[model_name] = jigna.models[model_name];
            }
            jigna.fire_event(jigna, 'object_changed');
        };

        add_to_scope(jigna.models);

        jigna.add_listener('jigna', 'context_updated', function(event){
            add_to_scope(event.data);
        });

        // Listen to object change events in jigna
        jigna.add_listener(jigna, 'object_changed', function() {
            if ($rootScope.$$phase === null){
                $rootScope.$digest();
            }
        });

        // fixme: this is very ugly. remove this asap.
        $rootScope.recompile = function(element) {
            $compile(element)($rootScope);

            jigna.fire_event(jigna, 'object_changed');
        };

    }]);

    return module;
});
