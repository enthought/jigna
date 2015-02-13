"""
This example shows how to embed a jigna view to an existing QWidget framework.
"""

#### Imports ####

from traits.api import HasTraits, Int, Str
from jigna.api import Template, QtApp

#### Domain model ####

class Employee(HasTraits):
    name = Str
    salary = Int

    def update_salary(self):
        self.salary += int(0.2*self.salary)

#### UI layer ####

body_html = """
    <div>
      Employee name is {{employee.name}}<br/>
      Salary is ${{employee.salary}}<br/>

      <button ng-click='employee.update_salary()'>
        Update salary
      </button>
    </div>
"""

template = Template(body_html=body_html)

def show_embedded_window(widget):
    """ Create and show a QMainWindow which embeds the given widget on a button
    click. This is a *blocking* call.
    """
    from jigna.qt import QtGui
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
    tom = Employee(name='Tom', salary=2000)

    # Create a QtApp to render the HTML template with the given context.
    app = QtApp(template=template, context={'employee': tom})

    # Create the control from the QtApp
    widget = app.create_widget()

    # Embed the widget created above to another Qt window.
    show_embedded_window(widget)

    # Check the values after the UI is closed
    print tom.name, tom.salary

if __name__ == "__main__":
    main()

#### EOF ######################################################################
