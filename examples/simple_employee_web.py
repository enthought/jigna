from traits.api import HasTraits, Str, Bool, Float, Enum
from jigna.html_view import HTMLView
from jigna.web_session import serve

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

view = HTMLView(model=sam)
# Now serve on the web but run the server on a separate thread.
serve(views=[view], thread=True)
# Also show the usual traitsui.
sam.configure_traits()
