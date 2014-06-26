"""
This example shows how to embed a jigna view to an existing QWidget framework.
"""

#### Imports ####

from traits.api import HasTraits, Int, Str
from pyface.qt import QtGui
from jigna.api import View

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

person_view = View(body_html=body_html)

#### Entry point ####

def main():
    # Start a QtGui application
    app = QtGui.QApplication([])

    # Define a new QMainWindow
    window = QtGui.QMainWindow()

    layout = QtGui.QVBoxLayout()
    layout.addWidget(QtGui.QPushButton("Qt button"))

    # Instantiate the domain model
    fred = Person(name='Fred', age=42)

    # Render the view with the domain model added to the context
    jigna_widget = person_view.create_widget(context={'person': fred})

    # Add the jigna widget to the window
    layout.addWidget(jigna_widget)

    # Set up the layout
    window.setCentralWidget(QtGui.QWidget())
    window.centralWidget().setLayout(layout)

    # Show the window
    window.show()

    # Start the event loop
    app.exec_()

    # Check the values after the UI is closed
    print fred.name, fred.age

if __name__ == "__main__":
    main()

#### EOF ######################################################################
