from traits.api import HasTraits, Instance, Int, Str, List
from jigna.api import JignaView
from pyface.qt import QtGui
from pyface.api import GUI

#### Domain model ####

class Person(HasTraits):
    name = Str
    age  = Int
    fruits = List(Str)

#### UI layer ####

html = """
    <div>
        Name: <input ng-model="model.name">
        Age: <input ng-model="model.age" type='number'>
        <br/>
        Fruits:
            <ul>
                <li ng-repeat="fruit in model.fruits"> {{fruit}} </li>
            </ul>
    </div>
"""

person_view = JignaView(html=html)

#### Entry point ###

def main():
    def listener(obj, traitname, old, new):
        print obj, traitname, old, new

    fred = Person(name='Fred', age=42)
    fred.on_trait_change(listener)
    fred.fruits = ["apple", "orange"]

    def set_fruits():
        fred.fruits = ["banana", "kiwi"]

    def update_fruits():
        fred.fruits.append("apple")

    app = QtGui.QApplication.instance() or QtGui.QApplication([])
    GUI.invoke_after(3000, set_fruits)
    GUI.invoke_after(4000, update_fruits)

    person_view.show(model=fred)
    app.exec_()
    print fred.fruits

if __name__ == "__main__":
    main()
