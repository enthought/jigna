from os.path import dirname, abspath

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

view = HTMLView(model=sam, model_name="sam")
serve([view], thread=True,
      html_template=open('test.html').read(),
      base_url=abspath(dirname(__file__)))
sam.configure_traits()