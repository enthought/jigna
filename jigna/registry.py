registry = {'models': {}, 'model_names': {}, 'model_classes': [], 'views': {}}

def add_model(model_name, model):
    global registry
    registry['models'][model_name] = model
    registry['model_names'][id(model)] = model_name

def remove_model(model):
    global registry
    model_name = registry['model_names'][id(model)]
    registry['model_names'].pop(id(model))
    registry['models'].pop(model_name)

def add_view(model_name, view):
    global registry
    registry['views'][model_name] = view

def remove_view(model_name):
    global registry
    registry['views'].pop(model_name)

def add_model_class(cls):
    global registry
    if not cls in registry['model_classes']:
        registry['model_classes'].append(cls)

def remove_model_class(cls):
    global registry
    registry['model_classes'].remove(cls)

def clean():
    global registry
    registry = {'models': {}, 'model_names': {}, 'model_classes':[], 'views': {}}
