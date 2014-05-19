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

require(['angular', 'jigna-angular'], function(angular, jigna_app){
    // Bootstrap the jigna-angular application when the document is ready
    $(document).ready(function(){
        angular.bootstrap(document, [jigna_app.name]);
    });
});
