""" This example shows the ability to view generic Python objects (not just
HasTraits objects) in HTML using Jigna. The data binding will only be one-way
in this case, i.e. from the UI to the model.
"""

#### Imports ####

from pyface.qt import QtGui
from jigna.api import View

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

person_view = View(body_html=body_html)

#### Entry point ####

def main():
    # Create the QtGui application object
    app = QtGui.QApplication([])

    # Instantiate the domain model
    fred = Person(name='Fred', age=42)

    # Create and show a QWidget which renders the HTML view with the domain
    # model added to its context.
    widget = person_view.create_widget(context={'person': fred})
    widget.show()

    # Start the event loop
    app.exec_()

    # Check the values after the UI is closed
    print fred.name, fred.age

if __name__ == "__main__":
    main()

#### EOF ######################################################################
