## Slow method call example ###################################################
# This example calls a method in Python world which is very slow and demonstra-
# tes that the UI does not block.
###############################################################################

from traits.api import HasTraits, Int, Str
from jigna.api import JignaView
from pyface.qt import QtGui
from pyface.timer.api import do_after

#### Domain model ####

import time

class Person(HasTraits):
    name = Str
    age  = Int

    power = Int

    def install_new_power(self):
        print "Installing new power...."
        
        while self.power < 100:
            time.sleep(0.5)
            self.power += 10
            print "Power increased to: ", self.power

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

person_view = JignaView(body_html=body_html, head_html=head_html)

#### Entry point ####

def main():
    fred  = Person(name='Fred', age=42)

    app = QtGui.QApplication.instance() or QtGui.QApplication([])
    person_view.show(model=fred)
    app.exec_()
    print fred.name, fred.age

    return

if __name__ == '__main__':
    main()

#### EOF ######################################################################
