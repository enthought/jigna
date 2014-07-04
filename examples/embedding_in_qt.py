"""
This example shows how to embed a jigna view to an existing QWidget framework.
"""

#### Imports ####

from traits.api import HasTraits, Int, Str
from jigna.api import Template, QtApp

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

def show_embedded_window(widget):
    """ Create and show a QMainWindow which embeds the given widget on a button
    click. This is a *blocking* call.
    """
    from pyface.qt import QtGui
    app = QtGui.QApplication.instance() or QtGui.QApplication([])

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

    # Show the window
    window.show()

    app.exec_()

#### Entry point ####

def main():
    # Instantiate the domain model
    fred = Person(name='Fred', age=42)

    # Create a QtApp to render the HTML template with the given context.
    app = QtApp(template=template, context={'person': fred})

    # Create the control from the QtApp
    widget = app.create_widget()

    # Embed the widget created above to another Qt window.
    show_embedded_window(widget)

    # Check the values after the UI is closed
    print fred.name, fred.age

if __name__ == "__main__":
    main()

#### EOF ######################################################################
