"""
This example demonstrates Jigna's ability to call public methods of the
traits model from the HTML interface. You can supply primitive arguments and
also pass instances.
"""

#### Imports ####
from __future__ import print_function

from traits.api import HasTraits, Int, Str, Instance
from jigna.api import HTMLWidget, Template
from jigna.qt import QtGui

#### Domain model ####

class Person(HasTraits):
    name = Str
    age = Int
    spouse = Instance('Person')

    def greet(self):
        """ Simple method without any arguments. """
        print('Greetings %s, from the Javascript world!' % self.name)

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

template = Template(body_html=body_html)

#### Entry point ####

def main():
    # Start the Qt application
    app = QtGui.QApplication([])

    # Instantiate the domain models
    fred = Person(name='Fred', age=14)
    wilma = Person(name='Wilma', age=25)

    # Create the jigna based HTML widget which renders the given HTML template
    # with the given context.
    widget = HTMLWidget(
        template=template, context={'person': fred, 'spouse': wilma}
    )
    widget.show()

    # Start the event loop.
    #
    # Clicking on the buttons in the UI will make blocking calls to the
    # corresponding methods on the domain model. You can supply primitive as
    # well as instance objects as arguments of the method.
    app.exec_()

    # Check the final values after the UI is closed
    print(fred.name, fred.age, fred.spouse.name)

if __name__ == '__main__':
    main()

#### EOF ######################################################################
