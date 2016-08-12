"""
This example shows how to attach 'done' and 'error' callbacks to a slow
method call.
"""

#### Imports ####

from traits.api import HasTraits
from jigna.api import HTMLWidget, Template
from jigna.qt import QtGui
import time

#### Domain model ####

class Worker(HasTraits):

    def do_work(self):
        """ Simulate doing some work by sleeping a bit :) """
        time.sleep(1)

    def do_illegal_work(self):
        """ Simulate doing an illegal work that will raise an error """
        time.sleep(1)
        raise Exception("Illegal operation")

#### UI layer ####

template = Template(html_file='success_error_callbacks.html')

#### Entry point ####

def main():
    # Start the Qt application
    app = QtGui.QApplication([])

    # Instantiate the domain models
    worker = Worker()

    # Create the jigna based HTML widget which renders the given HTML template
    # with the given context.
    widget = HTMLWidget(template=template, context={'worker': worker})
    widget.show()

    # Start the event loop.
    #
    # The view related code is such that clicking on the buttons in the UI will
    # call methods on the domain model and do something when the method call
    # succeeded or failed.
    app.exec_()

if __name__ == '__main__':
    main()

#### EOF ######################################################################
