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
    # Create the QtGui application object
    app = QtGui.QApplication([])

    # Instantiate the domain model
    fred = Person(name='Fred')
    wilma = Person(name='Wilma')

    # Create and show a QWidget which renders the HTML view with the domain
    # models added to its context.
    #
    # Initially, the `spouse` field of the person is empty, so the fields
    # related to the spouse should be empty in the UI.
    widget = person_view.create_widget(context={'person':fred})
    widget.show()

    # Schedule some operations on the domain model.
    #
    # The operation should fill in the `spouse` field of the person and this
    # should be reflected in the UI.
    from pyface.timer.api import do_after
    do_after(2500, fred.marry, wilma)

    # Start the event loop
    app.exec_()

    # Check the final values of the instance
    print fred.name, fred.spouse.name, wilma.name

if __name__ == "__main__":
    main()

#### EOF ######################################################################
