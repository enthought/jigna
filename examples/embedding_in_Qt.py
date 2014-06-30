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

def create_embedded_window(widget):
    """ Create a QMainWindow which embeds the given widget on a button click """

    # Define a new QMainWindow
    window = QtGui.QMainWindow()
    window.setMinimumSize(600, 400)

    # Set up the QLayout
    layout = QtGui.QVBoxLayout()
    window.setCentralWidget(QtGui.QWidget())
    window.centralWidget().setLayout(layout)

    # Add a button to the layout which embeds the supplied widget on click.
    button = QtGui.QPushButton("I'm a QPushButton. Press me to embed a widget")
    button.clicked.connect(lambda : layout.addWidget(widget))
    layout.addWidget(button)

    return window

def main():
    # Start a QtGui application
    app = QtGui.QApplication([])

    # Instantiate the domain model
    fred = Person(name='Fred', age=42)

    # Create a QWidget which renders the HTML view with the domain
    # models added to its context.
    widget = person_view.create_widget(context={'person': fred})

    # Embed the widget created above to another Qt window.
    window = create_embedded_window(widget)
    window.show()

    # Start the event loop
    app.exec_()

    # Check the values after the UI is closed
    print fred.name, fred.age

if __name__ == "__main__":
    main()

#### EOF ######################################################################
