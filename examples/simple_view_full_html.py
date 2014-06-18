"""
This example shows how to initialize Jigna's HTML interface by reading
a full html file, rather than specifying body_html and head_html.
"""

#### Imports ##################################################################

from traits.api import HasTraits, Int, Str
from pyface.qt import QtGui
from jigna.api import View

#### Domain model ####

class Person(HasTraits):
    name = Str
    age  = Int

    def update_name(self, name):
        self.name = name

#### UI layer ####

person_view = View(html_file='simple_view_full.html')

#### Entry point ####

def main():
    # Start a QtGui application
    app = QtGui.QApplication([])

    # Instantiate the domain model
    fred = Person(name='Fred', age=42)

    # Render the view with the domain model added to the context
    person_view.show(person=fred)

    # Start the event loop
    app.exec_()

    # Check the values after the UI is closed
    print fred.name, fred.age

if __name__ == "__main__":
    main()

#### EOF ######################################################################
