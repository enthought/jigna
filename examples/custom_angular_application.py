"""
This example shows how to use Jigna alongwith a custom angularjs application. We
would need a custom angularjs application to add some view related logic.
"""

#### Imports ####

from traits.api import HasTraits, Enum, Int
from pyface.qt import QtGui
from jigna.api import View
import time

#### Domain model ####

class StopWatch(HasTraits):
    state = Enum('stopped', 'running')
    time = Int

    def start(self):
        self.state = 'running'
        while self.state == 'running':
            time.sleep(1)
            self.time += 1

    def stop(self):
        self.state = 'stopped'

    def reset(self):
        self.time = 0

#### UI layer ####

clock_view = View(html_file='custom_angular_application.html')

#### Entry point ####

def main():
    # Start a QtGui application
    app = QtGui.QApplication([])

    # Instantiate the domain model
    clock = StopWatch()

    # Render the view with the domain model added to the context
    clock_view.show(clock=clock)

    # Start the event loop
    app.exec_()

    # Check the values after the UI is closed
    print clock.time, "seconds"

if __name__ == "__main__":
    main()

#### EOF ######################################################################
