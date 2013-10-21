var jigna = {};

///////////////////////////////////////////////////////////////////////////////
// ProxyManager
///////////////////////////////////////////////////////////////////////////////

jigna.ProxyManager = function(scope){
    // ProxyManager protocol.
    this.scope = scope;

    // Private protocol
    this._bridge          = window['python_bridge'];
    this._id_to_proxy_map = {};
    this._proxy_factory   = new jigna.ProxyFactory(this);
}

// ProxyManager protocol //////////////////////////////////////////////////////

jigna.ProxyManager.prototype.add_model = function(model_name, id) {
    // Get a proxy for the object identified by Id...
    var proxy = this.get_proxy('instance', id);

    // ... and expose it with the name 'model_name' to AngularJS.
    this._add_in_scope(model_name, proxy);
};

jigna.ProxyManager.prototype.get_proxy = function(type, value) {
    var proxy;
    if (type === 'primitive') {
	proxy = value;
    }
    else {
	proxy = this._id_to_proxy_map[value];
	if (proxy === undefined) {
	    proxy = this._proxy_factory.create_proxy(type, value);
	    this._id_to_proxy_map[value] = proxy;
	}
    };

    return proxy;
};

jigna.ProxyManager.prototype.on_trait_change = function(id, trait_name, value) {
    console.log('on trait change!!!!!!!!!!!!', id, trait_name, value);
    this.scope.$apply(function(){});
};

jigna.ProxyManager.prototype.on_list_items_change = function(id, trait_name, value) {
    this.scope.$apply(
        function() {
            //var list = jigna._id_to_proxy_map[id][trait_name];
            //list.splice.apply(list, value);
        }
    );
};


// Private protocol ///////////////////////////////////////////////////////////

jigna.ProxyManager.prototype._add_in_scope = function(model_name, proxy) {
    this.scope.$apply(
        function() {jigna.proxy_manager.scope[model_name] = proxy;}
    )
};

// fixme: Bridge object? Maye jigna *is* the bridge!
jigna.ProxyManager.prototype.bridge_get_trait_info = function(id) {
    console.log('get trait info for', id);
    return this._bridge.get_trait_info(id);
}

jigna.ProxyManager.prototype.bridge_get_trait = function(id, trait_name) {
    return this._bridge.get_trait(id, trait_name);
}

jigna.ProxyManager.prototype.bridge_set_trait = function(id, trait_name,value){
    return this._bridge.set_trait(id, trait_name, value);
}

///////////////////////////////////////////////////////////////////////////////
// ProxyFactory
///////////////////////////////////////////////////////////////////////////////

jigna.ProxyFactory = function(proxy_manager) {
    this.proxy_manager = proxy_manager;
};

jigna.ProxyFactory.prototype.create_proxy = function(type, value) {
    /* Make a proxy for the given value (typed by type!). */

    console.log('create_proxy', type, value);

    var proxy;

    if (type === 'instance' || type === 'list') {
	proxy = this._create_instance_proxy(value)
    }
    else {
	console.log('aaaaaggggggh')
    }

    return proxy;
};

//// Private protocol /////////////////////////////////////////////////////////

jigna.ProxyFactory.prototype._create_instance_proxy = function(id) {
    var proxy = new jigna.InstanceProxy(id, this.proxy_manager);
    var trait_names = this.proxy_manager.bridge_get_trait_info(id);
    for (var index in trait_names) {
	this._add_property(proxy, trait_names[index]);
    }

    return proxy;
}

jigna.ProxyFactory.prototype._add_property = function(proxy, trait_name){
    var descriptor = this._make_descriptor(proxy, trait_name);
    Object.defineProperty(proxy, trait_name, descriptor);
};

jigna.ProxyFactory.prototype._make_descriptor = function(proxy, trait_name){
    var get = function() {
	// In here, 'this' refers to the proxy!
	result = this.proxy_manager.bridge_get_trait(this.id, trait_name)
	if (result.exception != null) {
	    console.log('exception!!!!!!!!!!!', result.exception)
        }
	
	var value;
	if (result.type == 'primitive') {
	    value = result.value
	}
	else if (result.type == 'list' ) {
	    value = [];
	    for (var i in result.value) {
		var item_type  = result.value[i][0];
		var item_value = result.value[i][1];
		value.push(
		    this.proxy_manager.get_proxy(item_type, item_value)
		);
	    }

	    proxy = this.proxy_manager.get_proxy(result.type, result.value);
	    proxy.length = value.length;
	    value = proxy;
	    
	}
	else {
	    value = this.proxy_manager.get_proxy(result.type, result.value);
	};

	return value;
    };

    var set = function(value) {
	// In here, 'this' refers to the proxy!
	this.proxy_manager.bridge_set_trait(this.id, trait_name, value)
    };

    descriptor = {
        get          : get,
        set          : set,
        configurable : true,
        enumerable   : true,
        writeable    : true
    };

    return descriptor;
};

///////////////////////////////////////////////////////////////////////////////
// InstanceProxy
///////////////////////////////////////////////////////////////////////////////

jigna.InstanceProxy = function(id, proxy_manager) {
    this.id = id;
    this.proxy_manager = proxy_manager;
    this.length = 2;
};

///////////////////////////////////////////////////////////////////////////////

$(document).ready(function(){
    var scope = $(document.body).scope();
    jigna.proxy_manager = new jigna.ProxyManager(scope);
})

//// EOF //////////////////////////////////////////////////////////////////////

// jigna.ProxyManager.prototype.on_trait_change = function(id, trait_name, value) {
//     console.log("on trait change!!!!!!!!!!!!'", id, trait_name, value);
//     this.scope.$apply(
//         function() {
//             //jigna.proxy_manager._id_to_proxy_map[id][trait_name] = value;
//         }
//     );
// };

////////////////////////////////////----------------------------------
////////////////////////////////////----------------------------------
////////////////////////////////////----------------------------------
////////////////////////////////////----------------------------------
////////////////////////////////////----------------------------------
////////////////////////////////////----------------------------------
////////////////////////////////////----------------------------------
////////////////////////////////////----------------------------------
////////////////////////////////////----------------------------------
////////////////////////////////////----------------------------------
////////////////////////////////////----------------------------------
////////////////////////////////////----------------------------------
////////////////////////////////////----------------------------------
////////////////////////////////////----------------------------------
////////////////////////////////////----------------------------------
////////////////////////////////////----------------------------------
////////////////////////////////////----------------------------------
////////////////////////////////////----------------------------------
////////////////////////////////////----------------------------------
////////////////////////////////////----------------------------------
////////////////////////////////////----------------------------------
////////////////////////////////////----------------------------------
////////////////////////////////////----------------------------------
////////////////////////////////////----------------------------------

// jigna.ProxyFactory.prototype._XXXXmake_descriptor = function(id, trait_name, trait_info) {
//     var factories = {
//         "instance": this._make_instance_descriptor,
//         "primitive": this._make_primitive_descriptor,
//         "list_instance": this._make_list_instance_descriptor,
//         "list_primitive": this._make_primitive_descriptor
//     };
//     var factory = factories[trait_info["type"]];

//     return factory(id, trait_name);
// };

// jigna.ProxyFactory.prototype._make_instance_proxy = function(id) {
//     var proxy = new jigna.InstanceProxy(id);

//     var trait_info = JSON.parse(
//         this.proxy_manager._bridge.get_trait_info(id)
//     );

//     for (var trait_name in trait_info) {
//         this._add_property_to_proxy(
//             id, proxy, trait_name, trait_info[trait_name]
//         );
//     }

//     return proxy;
// }

// jigna.ProxyFactory.prototype._make_primitive_proxy = function(value) {
//     var proxy = value;

//     return proxy;
// }


// jigna.ProxyFactory.prototype._make_instance_descriptor = function(id, trait_name) {
//     var proxy_factory = this;
//     var get = function() {
//         return jigna.proxy_manager.get_proxy_from_id(trait_info["id"]);
//     };

//     var set = function(new_id) {
//         var info = {type: "instance", id: String(new_id)};
//         var descriptor = proxy_factory._make_descriptor(id, trait_name, info);
//         Object.defineProperty(this, trait_name, descriptor);
//     };

//     return {
//         enumerable: true,
//         writeable: true,
//         configurable: true,
//         get: get,
//         set: set
//     };
// };

// jigna.ProxyFactory.prototype._make_list_instance_descriptor = function(id, trait_name) {
//     var proxy_factory = this;
//     var get = function() {
//         var result = [];
//         var list_info = JSON.parse(
//             jigna.proxy_manager._bridge.get_trait(id, trait_name)
//         );
//         for (var index in list_info) {
//             result.push(jigna.proxy_manager.get_proxy(list_info[index]));
//         }
//         return result;
//     };

//     var set = function(new_ids) {
//         var info = {type: "list_instance",
//                     value: JSON.stringify(new_ids)};
//         var descriptor = proxy_factory._make_descriptor(id, trait_name, info);
//         Object.defineProperty(this, trait_name, descriptor);
//     };

//     return {
//         enumerable: true,
//         writeable: true,
//         configurable: true,
//         get: get,
//         set: set
//     };
// };

// jigna.ProxyFactory.prototype._make_primitive_descriptor = function(id, trait_name) {
//     var get = function() {
//         return JSON.parse(
//             jigna.proxy_manager._bridge.get_trait(id, trait_name)
//         );
//     };

//     var set = function(value) {
//         jigna.proxy_manager._bridge.set_trait(
//             id,
//             trait_name,
//             JSON.stringify(value)
//         );
//     };

//     return {
//         enumerable: true,
//         writeable: true,
//         configurable: true,
//         get: get,
//         set: set
//     };
// };

