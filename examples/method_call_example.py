from traits.api import HasTraits, Int, Str
from jigna.api import JignaView
from pyface.qt import QtGui
from pyface.timer.api import do_after

#### Domain model ####

class Person(HasTraits):
    name = Str
    age  = Int

    def do_something(self):
        print 'do something!!!!!!!!'

    def upper(self, name):
        self.name = name.upper()
        print 'upper', self.name

    def pass_instance(self, obj):
        print 'got obj', obj.name

#### UI layer ####

body_html = """
    <div>
      Name: <input ng-model="model.name">
      Age: <input ng-model="model.age" type='number'>
      <button ng-click="model.do_something()">Do Something!</button>
      <button ng-click="model.upper(model.name)">Upper</button>
      <button ng-click="model.pass_instance(model)">Pass Instance</button>
    </div>
"""

person_view = JignaView(body_html=body_html)

#### Entry point ####

def main():
    fred  = Person(name='Fred', age=42)

    app = QtGui.QApplication.instance() or QtGui.QApplication([])
    person_view.show(model=fred)

    app.exec_()

    return

if __name__ == '__main__':
    main()

#### EOF ######################################################################
