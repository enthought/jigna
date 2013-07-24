from traits.api import HasTraits, Str, Bool, List, Instance
from jigna.html_view import HTMLView
from jigna.session import show_simple_view

class SimpleEmployee(HasTraits):
    first_name = Str
    last_name = Str

    is_manager = Bool(False)

class Manager(SimpleEmployee):
    is_manager = Bool(True)

    subordinates = List(Instance(SimpleEmployee))

    def _subordinates_default(self):
        return [SimpleEmployee(first_name='Sam',
        					   last_name='Jackson'),
        		SimpleEmployee(first_name='Megan',
        					   last_name='Fox'),
        		SimpleEmployee(first_name='Foo',
        					   last_name='Employee')]

tom = Manager(first_name="Tom",
              last_name="Cruise")
ui = tom.edit_traits()


view = HTMLView(model=tom, model_name="tom")
show_simple_view(view)
