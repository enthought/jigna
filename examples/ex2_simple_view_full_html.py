"""
This example shows how to initialize Jigna's HTML interface by reading
a full html file, rather than specifying body_html and head_html.
"""

#### Imports ####
from __future__ import print_function

from traits.api import HasTraits, Int, Str
from jigna.api import HTMLWidget, Template
from jigna.qt import QtGui

#### Domain model ####

class Person(HasTraits):
    name = Str
    age  = Int

    def update_name(self, name):
        self.name = name

#### UI layer ####

template = Template(html_file='ex2_simple_view_full.html')

#### Entry point ####

def main():
    # Start the Qt application
    app = QtGui.QApplication([])

    # Instantiate the domain model
    fred = Person(name='Fred', age=42)

    # Create the jigna based HTML widget which renders the given HTML template
    # with the given context.
    widget = HTMLWidget(template=template, context={'person': fred})
    widget.show()

    # Start the event loop
    app.exec_()

    # Check the values after the UI is closed
    print(fred.name, fred.age)

if __name__ == "__main__":
    main()

#### EOF ######################################################################
