"""
This example demonstrates how updates to the application model's attributes are
reflected in the HTML view.
"""

#### Imports ####

from traits.api import HasTraits, Str
from pyface.qt import QtGui
from jigna.api import View

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

motd_view = View(body_html=body_html)

#### Entry point ####

def main():
    # Create the QtGui application object
    app = QtGui.QApplication([])

    # Instantiate the domain model
    motd = MOTD(message="Explicit is better than implicit.")

    # Create and show a QWidget which renders the HTML view with the domain
    # model added to its context.
    widget = motd_view.create_widget(context={'motd':motd})
    widget.show()

    # Schedule an update to a model variable after 2.5 seconds. This update
    # will be reflected in the UI immediately.
    from pyface.timer.api import do_after
    do_after(2500, motd.update_message, "Flat is better than nested.")

    # Start the event loop
    app.exec_()

if __name__ == "__main__":
    main()

#### EOF ######################################################################
