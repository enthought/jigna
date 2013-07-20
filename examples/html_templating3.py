from os.path import dirname, abspath

from traits.api import HasTraits, Str, Bool, Float, Enum
from jigna.html_view import HTMLView
from jigna.session import show_simple_view

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
ui = sam.edit_traits()

view = HTMLView(model=sam, model_name="sam")
show_simple_view(view,
                 html_template=open('test.html').read(),
                 base_url=abspath(dirname(__file__)))