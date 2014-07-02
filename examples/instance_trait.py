"""
This example shows two-way data binding on an `Instance` trait.
"""

#### Imports ####

from traits.api import HasTraits, Instance, Str
from jigna.api import Template, QtApp

#### Domain model ####

class Person(HasTraits):
    name = Str
    spouse = Instance('Person')

    def marry(self, person):
        self.spouse = person
        person.spouse = self

#### UI layer ####

body_html = """
    <div>
      Name: <input ng-model="person.name"><br/>
      Spouse's name: <input ng-model="person.spouse.name"><br/>
      Spouse's spouse's name: <input ng-model="person.spouse.spouse.name">
    </div>
"""

template = Template(body_html=body_html)


#### Entry point ####

def main():
    # Instantiate the domain model
    fred = Person(name='Fred')
    wilma = Person(name='Wilma')

    # Create a QtApp to render the HTML template with the given context.
    app = QtApp(template=template, context={'person':fred})

    # Schedule some operations on the domain model.
    #
    # The operation should fill in the `spouse` field of the person and this
    # should be reflected in the UI.
    from pyface.timer.api import do_after
    do_after(2500, fred.marry, wilma)

    # Start the event loop.
    #
    # Initially, the `spouse` field of the person is empty, so the fields
    # related to the spouse should be empty in the UI.
    app.start()

    # Check the final values of the instance
    print fred.name, fred.spouse.name, wilma.name

if __name__ == "__main__":
    main()

#### EOF ######################################################################
