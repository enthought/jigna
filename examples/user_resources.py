"""
This example shows how to add additional resources like CSS, javascript
and image files in your html by specifying a base url.
"""

#### Imports ##################################################################

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
        <img ng-src='{{person.name}}.png' /><br/>
        <div id="caption" class='red'>
            {{person.name}} - {{person.age}} years old
        </div>
    </div>

    <script type='text/javascript' src='color_change.js'></script>
    <link rel='stylesheet' href='colors.css' />
"""

# The base_url field specifies where to look when trying to get external
# resources(defaults to an empty string, i.e. the current directory)
person_view = View(body_html=body_html, base_url='user_resources_data/')

#### Entry point ####

def main():
    # Start a QtGui application
    app = QtGui.QApplication([])

    # Instantiate the domain model
    lena = Person(name='Lena', age=28)

    # Render the view with the domain model added to the context
    person_view.show(person=lena)

    # Start the event loop
    app.exec_()

if __name__ == "__main__":
    main()

#### EOF ######################################################################
