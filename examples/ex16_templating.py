"""
This example shows how to include HTML templates for creating reusable
components.
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

html = """
  <html ng-app='templating'>
    <head>
      <script type='text/javascript' src='/jigna/jigna.js'></script>
      <script type='text/javascript' src='ex16_templating.js'></script>
    </head>
    <body>
      <person-view person="fred"></person-view>
      <person-view person="wilma"></person-view>
    </body>
  </html>
"""

# The base_url field specifies where to look when trying to get external
# resources(defaults to an empty string, i.e. the current directory)
template = Template(html=html)

#### Entry point ####


def main():
    # Start the Qt application
    app = QtGui.QApplication([])

    # Instantiate the domain model
    fred = Person(name='Fred', age=28)
    wilma = Person(name='Wilma', age=25)

    # Create the jigna based HTML widget which renders the given HTML template
    # with the given context.
    widget = HTMLWidget(
        template=template, context={'fred': fred, 'wilma': wilma}
    )
    widget.show()

    # Start the event loop.
    #
    # You should see that the person-view component's template is rendered with
    # the correct domain models.
    app.exec_()

if __name__ == "__main__":
    main()

#### EOF ######################################################################
