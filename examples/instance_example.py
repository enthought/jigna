from traits.api import HasTraits, Instance, Int, Str
from jigna.api import JignaView
from pyface.qt import QtGui
from pyface.api import GUI

#### Domain model ####

class Person(HasTraits):
    name = Str
    age  = Int
    friend = Instance('Person')

#### UI layer ####

html = """
    <div>
        Name: <input ng-model="model.name">
        Age: <input ng-model="model.age" type='number'>
        <br/>
        Friend name: <input ng-model="model.friend.name">
        <br/>
        Friend age: <input ng-model="model.friend.age" type='number'>
    </div>
"""

person_view = JignaView(html=html)

#### Entry point ###

def main():
    def listener(obj, traitname, old, new):
        print obj, traitname, old, new

    fred  = Person(name='Fred', age=42)
    fred.on_trait_change(listener)
    fred.friend = Person(name='Wilma', age=34)
    def update_friend():
        fred.friend.name = "Barney"
        fred.friend.age = 41
    app = QtGui.QApplication.instance() or QtGui.QApplication([])
    #GUI.invoke_after(3000, update_friend)
    person_view.show(model=fred)
    app.exec_()
    print fred.name
    print fred.age

if __name__ == "__main__":
    main()
