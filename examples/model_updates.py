"""
This example demonstrates how updates to the application model's attributes are
reflected in the HTML view.
"""

#### Imports ####

from traits.api import HasTraits, Str
from jigna.api import HTMLWidget, Template
from jigna.qt import QtGui
from jigna.utils.gui import do_after

#### Domain model ####

class MOTD(HasTraits):
    message = Str

    def update_message(self, message):
        self.message = message

#### UI layer ####

body_html = """
    <div>
      Message of the day: {{motd.message}}
    </div>
"""

template = Template(body_html=body_html)

#### Entry point ####

def main():
    # Start the Qt application
    app = QtGui.QApplication([])

    # Instantiate the domain model
    motd = MOTD(message="Explicit is better than implicit.")

    # Create the jigna based HTML widget which renders the given HTML template
    # with the given context.
    widget = HTMLWidget(template=template, context={'motd':motd})
    widget.show()

    # Schedule an update to a model variable after 2.5 seconds. This update
    # will be reflected in the UI immediately.
    do_after(2500, motd.update_message, "Flat is better than nested.")

    # Start the event loop
    app.exec_()

if __name__ == "__main__":
    main()

#### EOF ######################################################################
