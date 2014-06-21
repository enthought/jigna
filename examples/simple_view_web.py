"""
This example shows how to serve a simple jigna view over the web.
"""

#### Imports ####

from traits.api import HasTraits, Int, Str
from jigna.api import View

#### Domain model ####

class Person(HasTraits):
    name = Str
    age  = Int

#### UI layer ####

body_html = """
    <div>
      Name: <input ng-model="person.name"><br>
      Age: <input ng-model="person.age" type='number'>
    </div>
"""

person_view = View(body_html=body_html)

#### Entry point ####

def main():
    # Instantiate the domain model
    fred = Person(name='Fred', age=42)

    # Start serving the view with the domain model added to the context
    #
    # Point your web browser to http://localhost:8888/ to connect to the jigna
    # view. Any operation performed on the view there directly update the model
    # attributes here.
    person_view.serve(8888, person=fred)

    # Check the values after the UI is closed
    print fred.name, fred.age

if __name__ == "__main__":
    main()

#### EOF ######################################################################
