"""
This example shows how to initialize Jigna's HTML interface by reading
a full html file, rather than specifying body_html and head_html.
"""

#### Imports ####

from traits.api import HasTraits, Int, Str
from jigna.api import Template, QtApp

#### Domain model ####

class Person(HasTraits):
    name = Str
    age  = Int

    def update_name(self, name):
        self.name = name

#### UI layer ####

template = Template(html_file='simple_view_full.html')

#### Entry point ####

def main():
    # Instantiate the domain model
    fred = Person(name='Fred', age=42)

    # Create a QtApp to render the HTML template with the given context.
    app = QtApp(template=template, context={'person': fred})

    # Start the event loop
    app.start()

    # Check the values after the UI is closed
    print fred.name, fred.age

if __name__ == "__main__":
    main()

#### EOF ######################################################################
