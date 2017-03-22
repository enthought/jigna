"""
This example shows two-way data binding on an `Instance` trait.
"""

#### Imports ####
from __future__ import print_function

from traits.api import HasTraits, Instance, Str
from jigna.api import HTMLWidget, Template
from jigna.qt import QtGui
from jigna.utils.gui import do_after

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
    # Start the Qt application
    app = QtGui.QApplication([])

    # Instantiate the domain model
    fred = Person(name='Fred')
    wilma = Person(name='Wilma')

    # Create the jigna based HTML widget which renders the given HTML template
    # with the given context.
    widget = HTMLWidget(template=template, context={'person':fred})
    widget.show()

    # Schedule some operations on the domain model.
    #
    # The operation should fill in the `spouse` field of the person and this
    # should be reflected in the UI.
    do_after(2500, fred.marry, wilma)

    # Start the event loop.
    #
    # Initially, the `spouse` field of the person is empty, so the fields
    # related to the spouse should be empty in the UI.
    app.exec_()

    # Check the final values of the instance
    print(fred.name, fred.spouse.name, wilma.name)

if __name__ == "__main__":
    main()

#### EOF ######################################################################
