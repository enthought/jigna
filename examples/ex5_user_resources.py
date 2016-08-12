"""
This example shows how to add additional resources like CSS, javascript
and image files in your html by specifying a base url.
"""

#### Imports ####

from traits.api import HasTraits, Int, Str
from jigna.api import HTMLWidget, Template
from jigna.qt import QtGui

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
template = Template(body_html=body_html, base_url='ex5_data/',
    recommended_size=(600, 600)
)

#### Entry point ####

def main():
    # Start the Qt application
    app = QtGui.QApplication([])

    # Instantiate the domain model
    lena = Person(name='Lena', age=28)

    # Create the jigna based HTML widget which renders the given HTML template
    # with the given context.
    widget = HTMLWidget(template=template, context={'person':lena})
    widget.show()

    # Start the event loop.
    #
    # You should see that user resources like CSS, images and custom JS are
    # pulled in properly from the `user_resources_data` directory and displayed
    # in the view.
    app.exec_()

if __name__ == "__main__":
    main()

#### EOF ######################################################################
