"""
This example shows two-way data binding on an `Instance` trait.
"""

#### Imports ##################################################################

from traits.api import HasTraits, Instance, Str
from pyface.qt import QtGui
from jigna.api import View

#### Domain model ####

class Person(HasTraits):
    name = Str
    friend = Instance('Person')

    def make_friends(self, person):
        """ Makes self and the person friends with each other. """
        self.friend = person
        person.friend = self

#### UI layer ####

body_html = """
    <div>
      Name: <input ng-model="person.name"><br/>
      Friend's name: <input ng-model="person.friend.name"><br/>
      Friend's friend's name: <input ng-model="person.friend.friend.name">
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
    do_after(2500, fred.make_friends, wilma)

    # Start the event loop
    app.exec_()

    # Check the final values of the instance
    print fred.name, fred.friend.name

if __name__ == "__main__":
    main()

#### EOF ######################################################################
