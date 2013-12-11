"""This example demonstrates a progress bar to show how the UI is not
blocked during a slow method call. This is because the method calls are
performed in a separate thread.
"""

#### Imports ##################################################################

from traits.api import HasTraits, Int, Str
from pyface.qt import QtGui
from jigna.api import View

#### Utility function    ######################################################
def parse_command_line_args(argv=None, description="Example"):
    import argparse
    parser = argparse.ArgumentParser(
        description=description,
        add_help=True
        )
    parser.add_argument("--web",
                        help="Run the websocket version by starting a tornado server\
                        on port 8888",
                        action="store_true")
    args = parser.parse_args(argv)
    return args


#### Domain model ####

import time

class Person(HasTraits):
    name = Str
    age  = Int

    power = Int

    def install_new_power(self):
        from jigna.api import Future

        f = Future(self._install_new_power)
        f.on_done(self._install_completed)

    def _install_new_power(self):
        print "Installing new power...."

        while self.power < 100:
            time.sleep(0.5)
            self.power += 10
            print "Power increased to: ", self.power

    def _install_completed(self, value):
        print "Superpower installed"
        self.name = 'Batman'
        self.age = 400

#### UI layer ####

head_html = """
    <style type="text/css">
        .progress-bar-container {
            width: 100%;
            height: 10px;
            border: solid 1px #999;
            background-color: white;
            margin: 10px;
        }
        .completed-progress {
            background-color: blue;
            height: 100%;
        }
    </style>
"""

body_html = """
    <div>
      Name: <input ng-model="model.name">
      Age: <input ng-model="model.age" type='number'>
      Power: {{model.power}}
      <button ng-click="model.install_new_power()">Install new power!</button>

      <div class='progress-bar-container'>
        <div class='completed-progress' ng-style="{ width: model.power + '%' }"></div>
      </div>

    </div>
"""

person_view = View(body_html=body_html, head_html=head_html)

#### Entry point ####

def main():
    fred  = Person(name='Fred', age=42)

    args = parse_command_line_args(description=__doc__)
    if args.web:
        person_view.serve(model=fred)
    else:
        app = QtGui.QApplication.instance() or QtGui.QApplication([])
        person_view.show(model=fred)
        app.exec_()

    print fred.name, fred.age

    return

if __name__ == '__main__':
    main()

#### EOF ######################################################################
