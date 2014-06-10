require.config({
    paths: {
        'jquery': 'external/jquery.min',
        'angular': 'external/angular.min',
        'jigna': 'app/jigna',
        'jigna-angular': 'app/jigna-angular',
        'event_target': 'app/event_target',
        'subarray': 'app/subarray',
        'qt_bridge': 'app/qt_bridge',
        'web_bridge': 'app/web_bridge',
        'client': 'app/client',
        'async_client': 'app/async_client',
        'proxy_factory': 'app/proxy_factory',
        'proxy': 'app/proxy',
        'list_proxy': 'app/list_proxy'
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
