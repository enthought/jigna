registry = {'objects': {}, 'classes': []}

def add_object(obj):
    global registry
    registry['objects'][id(obj)] = obj

def remove_object(obj):
    global registry
    registry['objects'].pop(id(obj))

def add_class(cls):
    global registry
    if not cls in registry['classes']:
        registry['classes'].append(cls)

def remove_class(cls):
    global registry
    registry['classes'].remove(cls)

def clean():
    global registry
    registry = {'objects': {}, 'classes':[]}
