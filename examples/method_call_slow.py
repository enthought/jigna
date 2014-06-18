""" This example demonstrates a progress bar to show how the UI is not
blocked during a slow method call. This is because the method calls are
performed in a separate thread.
"""

#### Imports ##################################################################

from traits.api import HasTraits, Int, Str, Instance
from pyface.qt import QtGui
from jigna.api import View
import time

#### Domain model ####

class App(HasTraits):
    name = Str
    version = Str

class Installer(HasTraits):
    current = Instance('App')
    progress = Int

    def install(self, app):
        self.current = app
        while self.progress < 100:
            time.sleep(0.5)
            self.progress += 10

#### UI layer ####

body_html = """
    <div>
        <!-- Show a button to install in a thread -->
        <button ng-show="installer.progress==0"
                ng-click="jigna.threaded(installer, 'install', new_app)">
            Install {{new_app.name}}-{{new_app.version}}
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

installer_view = View(body_html=body_html)

#### Entry point ####

def main():
    # Start a QtGui application
    app = QtGui.QApplication([])

    # Instantiate the domain models
    installer = Installer()
    pandas = App(name='Pandas', version='1.0')

    # Render the view with the domain models added to the context
    installer_view.show(installer=installer, new_app=pandas)

    # Start the event loop
    app.exec_()

    # Check the final values
    print installer.current.name, installer.current.version

if __name__ == '__main__':
    main()

#### EOF ######################################################################
