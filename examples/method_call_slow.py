"""
This example shows how to call slow methods of the application model such
that the UI doesn't block while the method is executing. We present an API to
call such methods in a thread.

Note: It's the user's responsibility to make sure that there aren't thread
safety related issues with that method.
"""

#### Imports ####
from __future__ import print_function

from traits.api import HasTraits, Int, Str, Instance
from jigna.api import HTMLWidget, Template
from jigna.qt import QtGui
import time

#### Domain model ####

class Package(HasTraits):
    name = Str
    version = Str

class Installer(HasTraits):
    current = Instance('Package')
    progress = Int

    def install(self, package):
        self.current = package
        while self.progress < 100:
            time.sleep(0.5)
            self.progress += 10

#### UI layer ####

body_html = """
    <div>
        <!-- Show a button initially to install in a thread -->
        <button ng-show="installer.progress==0"
                ng-click="jigna.threaded(installer, 'install', new_package)">
            Install {{new_package.name}}-{{new_package.version}}
        </button>

        <!-- Show an "Installing..." text while progress is between 0 and 100 -->
        <div ng-show="installer.progress > 0 && installer.progress < 100">
            Installing {{installer.current.name}}-{{installer.current.version}}...
        </div>

        <!-- Show "Done" when the progress is 100% -->
        <div ng-show="installer.progress >= 100">
            Done!
        </div>

        <!-- A graphical progress bar -->
        <div class='progress-bar-container'>
            <div class='completed-progress'
                 ng-style="{ width: installer.progress + '%' }">
            </div>
        </div>
    </div>

    <style type="text/css">
        .progress-bar-container {
            height: 10px;
            border: solid 1px gray;
            margin-top: 10px;
        }
        .completed-progress {
            background-color: blue;
            height: 100%;
        }
    </style>
"""

template = Template(body_html=body_html)

#### Entry point ####

def main():
    # Start the Qt application
    app = QtGui.QApplication([])

    # Instantiate the domain models
    installer = Installer()
    pandas = Package(name='Pandas', version='1.0')

    # Create the jigna based HTML widget which renders the given HTML template
    # with the given context.
    widget = HTMLWidget(
        template=template,
        context={'installer': installer, 'new_package': pandas}
    )
    widget.show()

    # Start the event loop.
    #
    # Clicking on the button in the UI will call the `install` method in a
    # thread so that the UI is still responsive while the method is executing.
    # The progress bar is also updated as the method progresses.
    app.exec_()

    # Check the final values
    print(installer.current.name, installer.current.version)

if __name__ == '__main__':
    main()

#### EOF ######################################################################
