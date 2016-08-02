var fs = require('fs');
var util = require('util');
var path = require('path');

function concatenate(options) {
    var base_url = options.base_url || "";
    var files = options.src;
    var dest = options.dest;

    var concat_str = "";

    // Start by wrapping everything inside an anonymous function
    if (options.wrap === true) {
        concat_str = concat_str + "(function (){\n\n";
    }

    // Concatenate all the files
    for (var i=0; i<files.length; i++) {
        file = files[i];
        concat_str = concat_str + fs.readFileSync(path.join(base_url, file)) + "\n\n";
    }

    // Export given namespaces to window
    for (var j=0; j<options.exports.length; j++) {
        _export = options.exports[j];
        // Adding string of type: 'window.jigna = jigna;'
        concat_str = concat_str + util.format("window.%s = %s;\n", _export, _export);
    }

    // End the anonymous function wrap
    if (options.wrap === true) {
        concat_str += "\n})();\n";
    }

    // Write the generated script
    fs.writeFileSync(dest, concat_str);
}

// jigna.js: this includes angular.js.
concatenate({
    base_url: 'src/',
    src: [
        // External dependencies
        'external/jquery.min.js',
        'external/angular.js',

        // Internal dependencies
        'app/event_target.js',

        // Namespace definition
        'app/jigna.js',

        // App files
        'app/client.js',
        'app/async_client.js',
        'app/proxy_factory.js',
        'app/async_proxy_factory.js',
        'app/proxy.js',
        'app/subarray.js',
        'app/list_proxy.js',
        'app/qt_bridge.js',
        'app/web_bridge.js',
        'app/jigna-angular.js',
    ],
    dest: 'dist/jigna.js',
    wrap: true,
    exports: [
        '$',
        'angular',
        'jigna'
    ]
});

// jigna-vue.js: this includes vue.js.
concatenate({
    base_url: 'src/',
    src: [
        // External dependencies
        'external/jquery.min.js',
        'external/vue.js',

        // Internal dependencies
        'app/event_target.js',

        // Namespace definition
        'app/jigna.js',

        // App files
        'app/client.js',
        'app/async_client.js',
        'app/proxy_factory.js',
        'app/async_proxy_factory.js',
        'app/proxy.js',
        'app/subarray.js',
        'app/list_proxy.js',
        'app/qt_bridge.js',
        'app/web_bridge.js',
        'app/jigna-vue.js',
    ],
    dest: 'dist/jigna-vue.js',
    wrap: true,
    exports: [
        '$',
        'Vue',
        'jigna'
    ]
});
