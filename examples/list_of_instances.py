"""
This example shows two-way data binding for the `List` traits whose items are of
an instance (non-primitive) type.
"""

#### Imports ####
from __future__ import print_function

from traits.api import HasTraits, Instance, Str, List
from jigna.api import HTMLWidget, Template
from jigna.qt import QtGui
from jigna.utils.gui import do_after

#### Domain model ####

class Person(HasTraits):
    name = Str

    friends = List(Instance('Person'))

#### UI layer ####

# Looping over the list of instances. No surprises here.
body_html = """
    <div>
      Name: {{person.name}} <br/>

      Friends:
      <div ng-repeat="friend in person.friends">
        <input ng-model="friend.name">
      </div>
    </div>
"""

template = Template(body_html=body_html)

#### Entry point ####

def main():
    # Start the Qt application
    app = QtGui.QApplication([])

    # Instantiate the domain model
    fred = Person(name='Fred', friends=[Person(name='Dino')])

    # Create the jigna based HTML widget which renders the given HTML template
    # with the given context.
    widget = HTMLWidget(template=template, context={'person':fred})
    widget.show()

    # Schedule some operations on the list.
    #
    # We're trying to append and insert instances in the list in the future.
    # This should be reflected in the UI.
    do_after(2500, fred.friends.append, Person(name='Wilma'))
    do_after(5000, fred.friends.insert, 0, Person(name='Barney'))

    # Start the event loop
    app.exec_()

    # Check the final values of the list attribute
    print([friend.name for friend in fred.friends])

if __name__ == "__main__":
    main()

#### EOF ######################################################################
