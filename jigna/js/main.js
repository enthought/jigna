require.config({
    baseUrl: '/jigna/',

    paths: {
        'jquery': 'external/jquery.min',
        'angular': 'external/angular.min',
        'jigna': 'app/jigna'
    },

    shim: {
        'jquery': {
            exports: 'jQuery'
        },

        'angular': {
            exports: 'angular',
            deps: ['jquery']
        },

        'jigna': {
            exports: 'jigna',
            deps: ['angular']
        }
    }
});

require(['jquery', 'angular', 'jigna'], function($, angular, jigna){

    ///////////////////////////////////////////////////////////////////////////////
    // AngularJS App for jigna
    ///////////////////////////////////////////////////////////////////////////////

    console.log("angular::", angular);
    var module = angular.module('jigna', []);

    // Add initialization function on module run time
    module.run(function($rootScope, $compile){

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

    });

    jigna.initialize();
});
