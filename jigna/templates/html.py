# Standard library imports
from mako.template import Template
from os.path import join, dirname

# Enthought library imports
from traits.api import Str, Bool, HasTraits

def to_html(obj, js="", css="", resource_url=""):
    """ Returns a default html template of the trait named tname defined in 
    the object obj.
    """
    template_src = join(dirname(__file__), 'html.mako')
    template = Template(filename=template_src)
    return template.render(obj_class=obj.__class__.__name__, obj_id=id(obj),
                           obj=obj, jignajs=js, jignacss=css, 
                           jquery=resource_url+"jquery.min.js", 
                           angularjs=resource_url+"angular.min.js")
                           
if __name__=="__main__":
    class Employee(HasTraits):
        first_name = Str
        last_name = Str
        is_manager = Bool(True)
    
    e = Employee(first_name="Foo", last_name="Bar", is_manager=True)
    print to_html(e)