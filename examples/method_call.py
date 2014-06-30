"""
This example demonstrates Jigna's ability to call public methods of the
traits model from the HTML interface. You can supply primitive arguments and
also pass instances.
"""

#### Imports ####

from traits.api import HasTraits, Int, Str, Instance
from pyface.qt import QtGui
from jigna.api import View

#### Domain model ####

class Person(HasTraits):
    name = Str
    age = Int
    spouse = Instance('Person')

    def greet(self):
        """ Simple method without any arguments. """
        print 'Greetings %s, from the Javascript world!' % self.name

    def update_age(self, age):
        """ Method which takes a primitive argument. """
        self.age = age

    def marry(self, person):
        """ Method which takes an instance argument. """
        self.spouse = person
        person.spouse = self

#### UI layer ####

body_html = """
    <div>
      Name: <input ng-model="person.name"> <br/>
      Age: {{person.age}} <br/>
      Spouse: {{person.spouse.name}} <br/>

      <button ng-click="person.greet()">Greet!</button>
      <button ng-click="person.update_age(25)">Grow old</button>
      <button ng-click="person.marry(spouse)">Marry</button>
    </div>
"""

person_view = View(body_html=body_html)

#### Entry point ####

def main():
    # Create the QtGui application object
    app = QtGui.QApplication([])

    # Instantiate the domain models
    fred = Person(name='Fred', age=14)
    wilma = Person(name='Wilma', age=25)

    # Create and show a QWidget which renders the HTML view with the domain
    # models added to its context.
    #
    # Clicking on the buttons in the UI will make blocking calls to the
    # corresponding methods on the domain model. You can supply primitive as
    # well as instance objects as arguments of the method.
    widget = person_view.create_widget(context={'person':fred, 'spouse':wilma})
    widget.show()

    # Start the event loop
    app.exec_()

    # Check the final values after the UI is closed
    print fred.name, fred.age, fred.spouse.name

if __name__ == '__main__':
    main()

#### EOF ######################################################################
