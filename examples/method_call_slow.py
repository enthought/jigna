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
    current_app = Instance('App')
    progress = Int

    def install(self, app):
        print "installing"
        self.current_app = app
        while self.progress < 100:
            time.sleep(0.5)
            self.progress += 10

#### UI layer ####

body_html = """
    <div>
        Current app: {{installer.current_app.name}}-{{installer.current_app.version}}

        <button ng-click="jigna.threaded(installer, 'install', new_app)"
                ng-show="installer.progress==0">
            Install {{new_app.name}}-{{new_app.version}}
        </button>

        <div class='progress-bar-container'>
            <div class='completed-progress'
                 ng-style="{ width: installer.progress + '%' }">
            </div>
        </div>
    </div>

    <style type="text/css">
        .progress-bar-container {
            height: 10px;
            border: solid 1px #999;
            background-color: white;
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
    print installer.current_app.name, installer.current_app.version

if __name__ == '__main__':
    main()

#### EOF ######################################################################
