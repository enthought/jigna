"""
This example shows two-way data binding for the `List` traits whose items are of
an instance (non-primitive) type.
"""

#### Imports ##################################################################

from traits.api import HasTraits, Instance, Str, List
from pyface.qt import QtGui
from jigna.api import View

#### Domain model ####

class Person(HasTraits):
    name = Str

    friends = List(Instance('Person'))

#### UI layer ####

# Looping over the list of instances here. No surprises here.
body_html = """
    <div>
      Name: {{person.name}} <br/>

      Friends:
      <div ng-repeat="friend in person.friends">
        <input ng-model="friend.name">
      </div>
    </div>
"""

person_view = View(body_html=body_html)

#### Entry point ####

def main():
    # Start a QtGui application
    app = QtGui.QApplication([])

    # Instantiate the domain model
    fred = Person(name='Fred', friends=[Person(name='Dino')])

    # Render the view with the domain model added to the context
    person_view.show(person=fred)

    # Schedule some operations on the list
    from pyface.timer.api import do_after
    do_after(2500, fred.friends.append, Person(name='Wilma'))
    do_after(5000, fred.friends.insert, 0, Person(name='Barney'))

    # Start the event loop
    app.exec_()

    # Check the final values of the list attribute
    print [friend.name for friend in fred.friends]

if __name__ == "__main__":
    main()

#### EOF ######################################################################
