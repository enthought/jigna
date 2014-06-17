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
    # Start a QtGui application
    app = QtGui.QApplication([])

    # Instantiate the domain model
    motd = MOTD(message="Explicit is better than implicit.")

    # Render the view with the domain model added to the context
    motd_view.show(motd=motd)

    # Call a method on the model after some time
    from pyface.timer.api import do_after
    do_after(2500, motd.update_message, "Flat is better than nested.")

    # Start the event loop
    app.exec_()

if __name__ == "__main__":
    main()

#### EOF ######################################################################
