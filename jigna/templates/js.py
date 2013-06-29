# Standard library imports
from mako.template import Template
from os.path import join, dirname

# Enthought library imports
from traits.api import Str, Bool, HasTraits

def to_js(obj):
    template_src = join(dirname(__file__), 'js.mako')
    template = Template(filename=template_src)
    return template.render(obj_class=obj.__class__.__name__,
                           obj=obj,
                           pyobj='pyobj_%s'%id(obj))

if __name__ == "__main__":
    class Employee(HasTraits):
        first_name = Str
        last_name = Str
        is_manager = Bool(True)
    
    e = Employee(first_name="Foo", last_name="Bar", is_manager=True)
    print to_js(e)
