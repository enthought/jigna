"""
This example shows how to use Jigna alongwith a custom angularjs application. We
would need a custom angularjs application to add some view related logic.
"""

#### Imports ####
from __future__ import print_function

from jigna.api import HTMLWidget, Template
from jigna.qt import QtGui
import time
from traits.api import HasTraits, Enum, Int

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

template = Template(html_file='ex17_custom_angular_application.html')

#### Entry point ####

def main():
    # Start the Qt application
    app = QtGui.QApplication([])

    # Instantiate the domain model
    stop_watch = StopWatch()

    # Create the jigna based HTML widget which renders the given HTML template
    # with the given context.
    #
    # The operations on the stop watch can be controlled from the UI. The view
    # related logic is such that it always displays the integer time of the
    # domain model in a proper hh:mm:ss format.
    widget = HTMLWidget(template=template, context={'stop_watch': stop_watch})
    widget.show()

    # Start the event loop
    app.exec_()

    # Check the values after the UI is closed
    print(stop_watch.time, "seconds")

if __name__ == "__main__":
    main()

#### EOF ######################################################################
