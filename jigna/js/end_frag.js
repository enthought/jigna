// NOTE: This is a fragment file which will be appended with
// more code during the build process. Don't change.

// This is done to support the synchronous public API as 
// described here: https://github.com/jrburke/almond

	//The modules for your project will be inlined above
    //this snippet. Ask almond to synchronously require the
    //module value for 'main' here and return it as the
    //value to use for the public API for the built file.
    return require('main');
}));