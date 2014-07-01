"""
This example is the simplest example which shows how to start a jigna view.
"""

#### Imports ####

from traits.api import HasTraits, Int, Str
from jigna.api import Template, QtApp

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

template = Template(body_html=body_html)

#### Entry point ####

def main():
    # Instantiate the domain model
    fred = Person(name='Fred', age=42)

    # Create a QtApp to render the HTML template with the given context.
    app = QtApp(template=template, context={'person': fred})

    # Start the event loop
    app.start()

    # Check the values after the UI is closed
    print fred.name, fred.age

if __name__ == "__main__":
    main()

#### EOF ######################################################################
