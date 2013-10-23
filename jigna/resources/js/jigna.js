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

jigna.ProxyManager.prototype.get_proxy = function(type, obj) {
    var proxy;
    if (type === 'primitive') {
        proxy = obj;
    }
    else {
        proxy = this._id_to_proxy_map[obj];
        if (proxy === undefined) {
            proxy = this._proxy_factory.create_proxy(type, obj);
            this._id_to_proxy_map[obj] = proxy;
        }
    }

    return proxy;
};

jigna.ProxyManager.prototype.on_model_changed = function(type, value) {
    console.log('on_model_changed:', type, value);

    if (type != 'primitive') {
        var proxy = this._proxy_factory.create_proxy(type, value);
        this._id_to_proxy_map[value] = proxy;
    }

    if (this.scope.$$phase === null){
        this.scope.$digest()
    }
};

// Private protocol ///////////////////////////////////////////////////////////

jigna.ProxyManager.prototype._add_in_scope = function(model_name, proxy) {
    this.scope.$apply(
        function() {jigna.proxy_manager.scope[model_name] = proxy;}
    )
};

// fixme: Bridge object? Maye jigna *is* the bridge!
jigna.ProxyManager.prototype.bridge_get_trait_info = function(id) {
    return this._bridge.get_trait_info(id);
}

jigna.ProxyManager.prototype.bridge_get_trait = function(id, trait_name) {
    result = this._bridge.get_trait(id, trait_name);
    if (result.exception != null) {
        console.log('exception!!!!!!!!!!!', result.exception)
    }

    return this.get_proxy(result.type, result.value);
}

jigna.ProxyManager.prototype.bridge_set_trait = function(id, trait_name,value){
    return this._bridge.set_trait(id, trait_name, JSON.stringify(value));
}

///////////////////////////////////////////////////////////////////////////////
// ProxyFactory
///////////////////////////////////////////////////////////////////////////////

jigna.ProxyFactory = function(proxy_manager) {
    this.proxy_manager = proxy_manager;
};

jigna.ProxyFactory.prototype.create_proxy = function(type, value) {
    /* Make a proxy for the given value (typed by type!). */

    var proxy;

    if (type === 'instance') {
        proxy = this._create_instance_proxy(value)
    }
    else if (type === 'list') {
        proxy = this._create_list_proxy(value);
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
        return this.proxy_manager.bridge_get_trait(this.id, trait_name)
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
};

jigna.ListProxy = function(id, proxy_manager) {
    var descriptor = {
        configurable : true,
        enumerable   : false,
        writeable    : true
    };

    descriptor.value = id;
    Object.defineProperty(this, 'id', descriptor);

    descriptor.value = proxy_manager;
    Object.defineProperty(this, 'proxy_manager', descriptor);
};

///////////////////////////////////////////////////////////////////////////////

$(document).ready(function(){
    var scope = $(document.body).scope();
    jigna.proxy_manager = new jigna.ProxyManager(scope);
})

// EOF ////////////////////////////////////////////////////////////////////////
