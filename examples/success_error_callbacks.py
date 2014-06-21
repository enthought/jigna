""" This example shows how to attach 'done' and 'error' callbacks to a slow
method call.
"""

#### Imports ####

from traits.api import HasTraits
from pyface.qt import QtGui
from jigna.api import View
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

worker_view = View(html_file='success_error_callbacks.html')

#### Entry point ####

def main():
    # Start a QtGui application
    app = QtGui.QApplication([])

    # Instantiate the domain models
    worker = Worker()

    # Render the view with the domain model added to the context
    worker_view.show(worker=worker)

    # Start the event loop
    app.exec_()

if __name__ == '__main__':
    main()

#### EOF ######################################################################
