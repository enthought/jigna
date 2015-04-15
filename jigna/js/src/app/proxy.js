///////////////////////////////////////////////////////////////////////////////
// Proxy
///////////////////////////////////////////////////////////////////////////////

jigna.Proxy = function(type, id, client) {
    // We use the '__attribute__' pattern to reduce the risk of name clashes
    // with the actuall attribute and methods on the object that we are a
    // proxy for.
    Object.defineProperty(this, '__type__',   {value : type});
    Object.defineProperty(this, '__id__',     {value : id});
    Object.defineProperty(this, '__client__', {value : client});
    Object.defineProperty(this, '__cache__',  {value : {}, writable: true});

    // The state for each attribute can be 'busy' or undefined, if 'busy' it
    // implies that the server is waiting to receive the value.
    Object.defineProperty(this, '__state__',  {value : {}});
};
