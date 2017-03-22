"""
This example shows how to embed a jigna view to an existing QWidget framework.
"""

#### Imports ####

from jigna.api import HTMLWidget, Template
from jigna.qt import QtGui
from traits.api import HasTraits, Int, Str

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

def create_jigna_widget():
    """ Create a jigna based HTML widget. This widget is embedded in a QtGui
    application.

    """
    # Instantiate the domain model
    tom = Employee(name='Tom', salary=2000)

    # Create the jigna based HTML widget which renders the given HTML template
    # with the given context.
    return HTMLWidget(template=template, context={'employee': tom})

#### Entry point ####

def main():
    """ Create and show a QMainWindow which embeds the given widget on a button
    click.

    """
    app = QtGui.QApplication([])

    # Define a new QMainWindow
    window = QtGui.QMainWindow()
    window.setMinimumSize(600, 400)

    # Set up the QLayout
    layout = QtGui.QVBoxLayout()
    window.setCentralWidget(QtGui.QWidget())
    window.centralWidget().setLayout(layout)

    # Add a button to the layout which embeds the supplied widget on click.
    button = QtGui.QPushButton("I'm a QPushButton. Press me to embed a widget")
    button.clicked.connect(lambda : layout.addWidget(create_jigna_widget()))
    layout.addWidget(button)

    # Show the window
    window.show()

    app.exec_()

if __name__ == "__main__":
    main()

#### EOF ######################################################################
