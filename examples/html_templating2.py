from os.path import dirname

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

html = """
    <div data-model-name="sam">
        <h3>Employee's name is <input ng-model="first_name"> {{last_name}}</h3>
        He works in the <span class="department_name">{{department}}</span>
        department, and obtains a salary of
        Rs. <input ng-model="salary" type="number"> per month.
    </div>
    """

css = """
    .department_name {
        color: #0645AD;
    }
    """
view = HTMLView(model=sam, model_name="sam", html=html, css=css)
show_simple_view(view)