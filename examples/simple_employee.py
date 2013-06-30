# configure_traits.py -- Sample code to demonstrate
from traits.api import HasTraits, Str, Bool, Float, Enum
from jigna.html_view import HTMLView

class SimpleEmployee(HasTraits):
    first_name = Str
    last_name = Str
    
    salary = Float
    is_manager = Bool(True)
    department = Enum("Engineering", "Management")
    

sam = SimpleEmployee(first_name="Dark", 
                     last_name="Knight", 
                     department="Engineering", 
                     salary=50000)
sam.edit_traits()
view = HTMLView(model=sam)
view.show()