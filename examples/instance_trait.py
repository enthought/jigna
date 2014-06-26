"""
This example shows two-way data binding on an `Instance` trait.
"""

#### Imports ####

from traits.api import HasTraits, Instance, Str
from pyface.qt import QtGui
from jigna.api import View

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

person_view = View(body_html=body_html)


#### Entry point ####

def main():
    # Start a QtGui application
    app = QtGui.QApplication([])

    # Instantiate the domain model
    fred = Person(name='Fred')
    wilma = Person(name='Wilma')

    # Render the view with the domain model added to the context
    person_view.show(person=fred)

    # Schedule some operations on the domain model
    from pyface.timer.api import do_after
    do_after(2500, fred.marry, wilma)

    # Start the event loop
    app.exec_()

    # Check the final values of the instance
    print fred.name, fred.spouse.name, wilma.name

if __name__ == "__main__":
    main()

#### EOF ######################################################################
