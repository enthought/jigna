""" This example shows the ability to view generic Python objects (not just
HasTraits objects) in HTML using Jigna. The data binding will only be one-way
in this case, i.e. from the UI to the model.
"""

#### Imports ####

from jigna.api import Template, QtView

#### Domain model ####

class Person(object):
    def __init__(self, name, age):
        self.name = name
        self.age = age

#### UI layer ####

body_html = """
  <div>
    Name: <input ng-model="person.name">
    Age: <input ng-model="person.age" type='number'>
  </div>
"""

template = Template(body_html=body_html)

#### Entry point ####

def main():
    # Instantiate the domain model
    fred = Person(name='Fred', age=42)

    # Create a QtView to render the HTML template with the given context.
    #
    # This will behave as a static page since we don't have the traits
    # machinery here to reflect model updates in the view.
    view = QtView(template=template, context={'person': fred})

    # Start the event loop
    view.start()

    # Check the values after the UI is closed
    print fred.name, fred.age

if __name__ == "__main__":
    main()

#### EOF ######################################################################
