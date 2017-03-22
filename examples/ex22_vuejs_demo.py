"""
This example shows how to use Jigna using the Vue.js Javascript framework,
instead of AngularJS.
"""

#### Imports ####
from __future__ import print_function

from traits.api import HasTraits, Int, Str, List, Instance
from jigna.api import HTMLWidget, VueTemplate
from jigna.qt import QtGui
from jigna.utils.gui import do_after

#### Domain model ####

class Person(HasTraits):
    name = Str
    age  = Int
    fruits = List(Str)
    friends = List(Instance('Person'))

    def add_fruit(self, name='fruit'):
        self.fruits.append(name)

    def remove_fruit(self, index):
        del self.fruits[index]

    def update_name(self, name):
        print("Name updated to", name)
        self.name = name

    def add_friend(self):
        self.friends.append(Person(name='Person', age=0))

    def remove_friend(self, index):
        del self.friends[index]

    def _fruits_items_changed(self, l_event):
        print(l_event.added, l_event.removed, l_event.index)

#### UI layer ####

#### Entry point ####

def main():
    # Start the Qt application
    app = QtGui.QApplication([])

    # Instantiate the domain model

    fred = Person(name='Fred', age=42, fruits=['pear', 'apple'])

    template = VueTemplate(html_file='vuejs_demo.html')

    # Create the jigna based HTML widget which renders the given HTML template
    # with the given context.
    widget = HTMLWidget(template=template, context={'person': fred}, debug=True)
    widget.show()

    # Schedule an update to a model variable after 2.5 seconds. This update
    # will be reflected in the UI immediately.
    do_after(2500, fred.update_name, "Guido")
    do_after(2500, fred.add_fruit)
    do_after(2500, fred.add_friend)

    # Start the event loop
    app.exec_()

    # Check the values after the UI is closed
    print(fred.name, fred.age, fred.fruits, fred.friends)

if __name__ == "__main__":
    main()

#### EOF ######################################################################
