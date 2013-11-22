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

    def do_heavy_work(self):
        print "Starting heavy work...."
        time.sleep(5)
        print "in different thread: name, age", self.name, self.age
        print "changing the name:"
        self.name = 'Wilma'
        print 'sleeping some more...'
        time.sleep(5)
        print "Done!"

#### UI layer ####

body_html = """
    <div>
      Name: <input ng-model="model.name">
      Age: <input ng-model="model.age" type='number'>
      <button ng-click="model.do_heavy_work()">Do Heavy Work!</button>
    </div>
"""

person_view = JignaView(body_html=body_html)

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
