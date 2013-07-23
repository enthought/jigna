from traits.api import HasTraits, Str, Bool, List
from jigna.html_view import HTMLView
from jigna.session import show_simple_view

class SimpleEmployee(HasTraits):
    first_name = Str
    last_name = Str

    is_manager = Bool(False)

    colleagues = List(Str)

    def _colleagues_default(self):
        return ['Mary', 'John', 'Sam']

sam = SimpleEmployee(first_name="Tom",
                     last_name="Cruise",
                     is_manager=True)
ui = sam.edit_traits()


view = HTMLView(model=sam, model_name="sam")
show_simple_view(view)
