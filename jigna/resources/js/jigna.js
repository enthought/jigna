var jigna = {};

///////////////////////////////////////////////////////////////////////////////
// ProxyManager
///////////////////////////////////////////////////////////////////////////////

jigna.ProxyManager = function(scope){
    // ProxyManager protocol.
    this.scope = scope;

    function l(event) {
	console.log('llllllllllllll', event.name);
    };
    this.scope.$on('', l);

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
    console.log('get proxy for', value);
    var proxy;
    if (type === 'primitive') {
	proxy = value;
	console.log('primitive - no proxy');
    }
    else {
	console.log(this._id_to_proxy_map);
	proxy = this._id_to_proxy_map[value];
	if (proxy === undefined) {
	    proxy = this._proxy_factory.create_proxy(type, value);
	    this._id_to_proxy_map[value] = proxy;
	}
	console.log(this._id_to_proxy_map, proxy);
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
    info = this._bridge.get_trait_info(id);
    console.log('bridge_get_trait_info:', id, info);
    return info;
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

    if (type === 'instance') {
	proxy = this._create_instance_proxy(value)
    }
    else if (type === 'list') {
	proxy = this._create_list_proxy(value);
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

jigna.ProxyFactory.prototype._create_list_proxy = function(id) {
    var proxy = new jigna.ListProxy(id, this.proxy_manager);
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
	//console.log('get', this.id, trait_name, 'result', result);

	var value;
	if (result.type == 'primitive') {
	    value = result.value
	}
	else if (result.type == 'list' ) {
	    value = this.proxy_manager.get_proxy(result.type, result.value);
	}
	else {
	    value = this.proxy_manager.get_proxy(result.type, result.value);
	};

	return value;
    };

    var set = function(value) {
	alert('setter');
	console.log('****************set', this.id, trait_name, 'value', value);
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
};

jigna.ListProxy = function(id, proxy_manager) {
    var descriptor = {
        configurable : true,
        enumerable   : false,
        writeable    : true
    };

    descriptor.value = id;
    Object.defineProperty(this, 'id', descriptor);

    descriptor.value = 2;
    Object.defineProperty(this, 'length', descriptor);

    descriptor.value = proxy_manager;
    Object.defineProperty(this, 'proxy_manager', descriptor);
};

//jigna.ListProxy.prototype = new Array();
//jigna.ListProxy.constructor = jigna.ListProxy;

///////////////////////////////////////////////////////////////////////////////

$(document).ready(function(){
    var scope = $(document.body).scope();
    jigna.proxy_manager = new jigna.ProxyManager(scope);
})

// EOF ////////////////////////////////////////////////////////////////////////
