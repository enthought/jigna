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

def embed_jigna_view(layout):
    """ Create a jigna widget and embed it to the given QLayout """
    # Instantiate the domain model
    fred = Person(name='Fred', age=42)

    # Render the view with the domain model added to the context
    jigna_widget = person_view.create_widget(context={'person': fred})

    # Add the jigna widget to the layout
    layout.addWidget(jigna_widget)

def main():
    # Create the QtGui application object
    app = QtGui.QApplication([])

    # Define a new QMainWindow
    window = QtGui.QMainWindow()
    window.setMinimumSize(600, 400)

    # Set up the QLayout
    layout = QtGui.QVBoxLayout()
    window.setCentralWidget(QtGui.QWidget())
    window.centralWidget().setLayout(layout)

    # Add a button to the layout which embeds the jigna widget on click.
    button = QtGui.QPushButton("I'm a QPushButton. Press me to embed a jigna widget")
    button.clicked.connect(lambda : embed_jigna_view(layout))
    layout.addWidget(button)

    # Show the window
    window.show()

    # Start the event loop
    app.exec_()

if __name__ == "__main__":
    main()

#### EOF ######################################################################
