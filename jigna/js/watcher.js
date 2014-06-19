var watchr = require('watchr'),
    exec = require('child_process').exec;

var path = 'src/';

// Watch a directory or file
console.log('Watching path:', path);

// Watch a the given path for changes and execute the build command whenever there
// is any change in the source
watchr.watch({
    path: path,
    listener: function(){
        console.log("Reloading...");

        var cmd = 'node build.js';
        exec(cmd, function(error, stdout, stderr){
            console.log(stdout);
            console.error(stderr);
            console.log("Done!");
        });
    }
});
