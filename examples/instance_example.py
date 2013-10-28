from traits.api import HasTraits, Instance, Int, Str
from jigna.api import JignaView
from pyface.qt import QtGui
from pyface.timer.api import do_after

#### Domain model ####

class Person(HasTraits):
    name = Str
    age  = Int
    friend = Instance('Person')

#### UI layer ####

body_html = """
    <div>
      Name: <input ng-model="model.name">
      Age: <input ng-model="model.age" type='number'>
      <br/>
      Friend name: <input ng-model="model.friend.name">
      <br/>
      Friend age: <input ng-model="model.friend.age" type='number'>
    </div>
"""

person_view = JignaView(body_html=body_html)

#### Entry point ####

def main():
    def listener(obj, traitname, old, new):
        print obj, traitname, old, new

    fred  = Person(name='Fred', age=42)
    fred.on_trait_change(listener)
    fred.friend = Person(name='Wilma', age=34)

    def update_friend():
        fred.friend.name = "Barney"
        fred.friend.age = 41

    def set_friend():
        print "Setting friend to Dino"
        fred.friend = Person(name="Dino", age=10)

    app = QtGui.QApplication.instance() or QtGui.QApplication([])
    do_after(3000, update_friend)
    do_after(4000, set_friend)

    person_view.show(model=fred)
    app.exec_()
    print fred.name
    print fred.age
    print fred.friend.name, fred.friend.age

if __name__ == "__main__":
    main()

#### EOF ######################################################################
