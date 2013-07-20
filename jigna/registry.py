registry = {'models': {}, 'model_names': {}, 'model_classes': [], 'views': {}}

def add_model(model_name, model):
    """ Add model `model` to the registry, and associate it with the name
    `model_name`.
    """
    global registry
    registry['models'][model_name] = model
    registry['model_names'][id(model)] = model_name

def remove_model(model):
    """ Remove model `model` from the registry.
    """
    global registry
    model_name = registry['model_names'][id(model)]
    registry['model_names'].pop(id(model))
    registry['models'].pop(model_name)

def add_view(model_name, view):
    """ Add HTMLView instance `view` to the registry, and associate it with the model
    named `model_name`.
    """
    global registry
    registry['views'][model_name] = view

def remove_view(model_name):
    """ Remove the view associated to `model_name` from the registry.
    """
    global registry
    registry['views'].pop(model_name)

def add_model_class(cls):
    """ Register specified class `cls` as a model class.
    """
    global registry
    if not cls in registry['model_classes']:
        registry['model_classes'].append(cls)

def remove_model_class(cls):
    """ Unregister model class `cls`.
    """
    global registry
    registry['model_classes'].remove(cls)

def clean():
    """ Clean the registry to pristine conditions.
    """
    global registry
    registry = {'models': {}, 'model_names': {}, 'model_classes':[], 'views': {}}
