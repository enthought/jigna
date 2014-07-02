"""
This example shows how to use Jigna alongwith a custom angularjs application. We
would need a custom angularjs application to add some view related logic.
"""

#### Imports ####

from traits.api import HasTraits, Enum, Int
from jigna.api import Template, QtApp
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

template = Template(html_file='custom_angular_application.html')

#### Entry point ####

def main():
    # Instantiate the domain model
    clock = StopWatch()

    # Create a QtApp to render the HTML template with the given context.
    #
    # The operations on the clock can be controlled from the UI. The view
    # related logic is such that it always displays the integer time of the
    # domain model in a proper hh:mm:ss format.
    app = QtApp(template=template, context={'clock':clock})

    # Start the event loop
    app.start()

    # Check the values after the UI is closed
    print clock.time, "seconds"

if __name__ == "__main__":
    main()

#### EOF ######################################################################
