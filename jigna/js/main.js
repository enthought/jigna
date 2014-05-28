require.config({
    baseUrl: '/jigna/',

    paths: {
        'jquery': 'external/jquery.min',
        'angular': 'external/angular.min',
        'jigna': 'app/jigna',
        'jigna-angular': 'app/jigna-angular'
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

define(['angular', 'jigna', 'jigna-angular'], function(angular, jigna){
    // Initialize jigna
    jigna.initialize();

    // Export the following namespaces to the global scope.
    window.angular = angular;
    window.jigna = jigna;
});
