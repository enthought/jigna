"""
This example shows how a toplevel model can be added dynamically to the jigna
view's context.

Note: This example is currently for INTERNAL testing purposes only as I couldn't
find a convincing use-case for this in real world applications.
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
      Person 1:
      <div>
        Name: <input ng-model="person1.name">
        Age: <input ng-model="person1.age" type='number'>
      </div>

      <br><br>

      Person 2:

      <!-- The object 'person2' won't be available to the view's context
      initially and would be added only dynamically later. -->
      <div>
        Name: <input ng-model="person2.name">
        Age: <input ng-model="person2.age" type='number'>
      </div>

    </div>
"""

person_view = View(body_html=body_html)

#### Entry point ####

def main():
    # Start a QtGui application
    app = QtGui.QApplication([])

    # Instantiate the domain model
    fred = Person(name='Fred', age=42)

    # Render the view with the domain model added to the context
    person_view.show(person1=fred)

    # Add a new person to the context after some time
    def add_person():
        wilma = Person(name='Wilma', age=25)
        person_view.update_context(person2=wilma)

    from pyface.timer.api import do_after
    do_after(2000, add_person)

    # Start the event loop
    app.exec_()

if __name__ == "__main__":
    main()

#### EOF ######################################################################
