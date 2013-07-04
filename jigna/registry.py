registry = {'models': {}, 'model_classes': [], 'views': {}}

def add_model(model):
    global registry
    registry['models'][id(model)] = model

def remove_model(model):
    global registry
    registry['models'].pop(id(model))

def add_view(model, view):
    global registry
    registry['views'][id(model)] = view

def remove_view(model, view):
    global registry
    registry['views'].pop(id(model))

def add_model_class(cls):
    global registry
    if not cls in registry['model_classes']:
        registry['model_classes'].append(cls)

def remove_model_class(cls):
    global registry
    registry['model_classes'].remove(cls)

def clean():
    global registry
    registry = {'models': {}, 'model_classes':[], 'views': {}}
