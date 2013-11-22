from traits.api import HasTraits, Int, Str
from jigna.api import WebSocketView
from pyface.qt import QtGui
from pyface.timer.api import do_after

#### Domain model ####

class Person(HasTraits):
    name = Str
    age  = Int

#### UI layer ####

body_html = """
    <div>
      Name: <input ng-model="model.name">
      Age: <input ng-model="model.age" type='number'>
    </div>
"""

person_view = WebSocketView(body_html=body_html)

#### Entry point ####

def main():
    def listener(obj, traitname, old, new):
        print obj, traitname, old, new

    fred  = Person(name='Fred', age=42)
    fred.on_trait_change(listener)
    def update_fred():
        fred.name = "Wilma"
        fred.age = 4

    app = QtGui.QApplication.instance() or QtGui.QApplication([])
    person_view.show(model=fred)
    do_after(2000, update_fred)
    app.exec_()
    print fred.name
    print fred.age

if __name__ == "__main__":
    main()

#### EOF ######################################################################
