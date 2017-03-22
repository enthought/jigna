"""
This example is the simplest example which shows how to start a jigna view.
"""

#### Imports ####
from __future__ import print_function

from jigna.api import HTMLWidget, Template
from jigna.qt import QtGui
from traits.api import HasTraits, Int, Str

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
    # Start a QtGui application
    app = QtGui.QApplication([])

    # Instantiate the domain model
    fred = Person(name='Fred', age=42)

    # Create a jigna based HTML widget to render the HTML template with the
    # given context.
    widget = HTMLWidget(template=template, context={'person': fred})
    widget.show()

    # Start the event loop
    app.exec_()

    # Check the values after the UI is closed
    print(fred.name, fred.age)

if __name__ == "__main__":
    main()

#### EOF ######################################################################
