from traits.api import HasTraits, Str, Bool, Float, Enum
from traitsui.api import View, Item
from jigna.html_view import HTMLView
from jigna.session import Session


class SimpleEmployee(HasTraits):
    first_name = Str
    last_name = Str

    salary = Float
    is_manager = Bool(True)
    department = Enum("Engineering", "Management")


view1 = View(Item(name='first_name'),
             Item(name='last_name'),
             Item(name='department'))


sam = SimpleEmployee(first_name="Dark",
                     last_name="Knight",
                     department="Engineering",
                     salary=50000)
sam.edit_traits()
view_sam = HTMLView(model=sam)

rachel = SimpleEmployee(first_name="Cat",
                        last_name="Woman",
                        department="Management",
                        salary=100000)
rachel.edit_traits()
view_rachel = HTMLView(model=rachel)

session = Session(views=[view_sam, view_rachel])
session.start()
