# configure_traits.py -- Sample code to demonstrate
from traits.api import HasTraits, Str, Bool, Float, Enum
from traitsui.api import View, Item, Group
from jigna.html_view import HTMLView
from jigna.session import Session


view1 = View(Group(
    Item(name='first_name'),
    Item(name='last_name'),
    Item(name='department'),
))


class SimpleEmployee(HasTraits):
    first_name = Str
    last_name = Str

    salary = Float
    is_manager = Bool(True)
    department = Enum("Engineering", "Management")
    # traits_view = view1

sam = SimpleEmployee(first_name="Dark",
                     last_name="Knight",
                     department="Engineering",
                     salary=50000)
# sam.configure_traits(view=view1)
ui = sam.edit_traits()
view_sam = HTMLView(model=sam, layout=view1)


session = Session(views=[view_sam])
session.start()
