from traits.api import HasTraits, Str, Bool, Instance
from jigna.html_view import HTMLView
from jigna.session import show_simple_view

class SimpleEmployee(HasTraits):
    first_name = Str
    last_name = Str

    is_manager = Bool(False)

class Manager(SimpleEmployee):
    subordinate = Instance(SimpleEmployee)

rachel = SimpleEmployee(first_name="Cat",
                     last_name="Woman",
                     is_manager=False)

bruce = Manager(first_name="Dark",
                last_name="Knight",
                is_manager=True,
                subordinate=rachel)
ui = bruce.edit_traits()

view = HTMLView(model=bruce, model_name="bruce")
show_simple_view(view)
