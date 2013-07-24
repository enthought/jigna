from traits.api import HasTraits, Str, Bool, List
from jigna.html_view import HTMLView
from jigna.web_session import serve

class SimpleEmployee(HasTraits):
    first_name = Str
    last_name = Str

    is_manager = Bool(False)

    colleagues = List(Str)

    def _colleagues_default(self):
        return ['Mary', 'John', 'Sam']

tom = SimpleEmployee(first_name="Tom",
                     last_name="Cruise",
                     is_manager=True)

view = HTMLView(model=tom, model_name="tom")
serve([view], thread=True)

tom.configure_traits()