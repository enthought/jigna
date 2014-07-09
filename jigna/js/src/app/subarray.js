// SubArray.js ////////////////////////////////////////////////////////////////
// (C) Copyright Juriy Zaytsev
// Source: 1. https://github.com/kangax/array_subclassing
//         2. http://perfectionkills.com/how-ecmascript-5-still-does-not-allow-
//            to-subclass-an-array/
///////////////////////////////////////////////////////////////////////////////

var makeSubArray = (function(){

    var MAX_SIGNED_INT_VALUE = Math.pow(2, 32) - 1,
        hasOwnProperty = Object.prototype.hasOwnProperty;

    function ToUint32(value) {
        return value >>> 0;
    }

    function getMaxIndexProperty(object) {
        var maxIndex = -1, isValidProperty;

        for (var prop in object) {

            // int conversion of the property
            int_prop = ToUint32(prop);

            isValidProperty = (
                String(int_prop) === prop &&
                int_prop !== MAX_SIGNED_INT_VALUE &&
                hasOwnProperty.call(object, prop)
            );

            if (isValidProperty && int_prop > maxIndex) {
                maxIndex = prop;
            }
        }
        return maxIndex;
    }

    return function(methods) {
        var length = 0;
        methods = methods || { };

        methods.length = {
            get: function() {
                var maxIndexProperty = +getMaxIndexProperty(this);
                return Math.max(length, maxIndexProperty + 1);
            },
            set: function(value) {
                var constrainedValue = ToUint32(value);
                if (constrainedValue !== +value) {
                    throw new RangeError();
                }
                for (var i = constrainedValue, len = this.length; i < len; i++) {
                    delete this[i];
                }
                length = constrainedValue;
            }
        };

        methods.toString = {
            value: Array.prototype.join
        };

        return Object.create(Array.prototype, methods);
    };
})();

jigna.SubArray = function() {
    var arr = makeSubArray();

    if (arguments.length === 1) {
        arr.length = arguments[0];
    }
    else {
        arr.push.apply(arr, arguments);
    }
    return arr;
};
