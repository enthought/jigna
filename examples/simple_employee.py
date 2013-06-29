# configure_traits.py -- Sample code to demonstrate
from traits.api import HasTraits, Str
from jigna.html_view import HTMLView

class SimpleEmployee(HasTraits):
    first_name = Str
    last_name = Str
    department = Str
    employee_number = Str

sam = SimpleEmployee(first_name="Dark", 
                     last_name="Knight", 
                     department="Superheroic Maneuvers", 
                     employee_number="666")
sam.edit_traits()
view = HTMLView(model=sam)
view.show()