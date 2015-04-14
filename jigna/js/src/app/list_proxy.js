///////////////////////////////////////////////////////////////////////////////
// ListProxy
///////////////////////////////////////////////////////////////////////////////

// ListProxy is handled separately because it has to do special handling
// to behave as regular Javascript `Array` objects
// See "Wrappers. Prototype chain injection" section in this article:
// http://perfectionkills.com/how-ecmascript-5-still-does-not-allow-to-subclass-an-array/

jigna.ListProxy = function(type, id, client) {

    var arr = new jigna.SubArray();

    // fixme: repetition of property definition
    Object.defineProperty(arr, '__type__',   {value : type});
    Object.defineProperty(arr, '__id__',     {value : id});
    Object.defineProperty(arr, '__client__', {value : client});
    Object.defineProperty(arr, '__cache__',  {value : [], writable: true});

    // The state for each attribute can be 'busy' or undefined, if 'busy' it
    // implies that the server is waiting to receive the value.
    Object.defineProperty(arr, '__state__',  {value : {}});

    return arr;
};
