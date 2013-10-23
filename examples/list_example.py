from traits.api import HasTraits, Instance, Int, Str, List
from jigna.api import JignaView
from pyface.qt import QtGui
from pyface.api import GUI

#### Domain model ####

class Person(HasTraits):
    name = Str
    age  = Int
    fruits = List(Str)
    friends = List(Instance('Person'))

#### UI layer ####

html = """
    <div>
        Name: <input ng-model="model.name">
        Age: <input ng-model="model.age" type='number'>
        <br/>
        Fruits:
            <ul>
                <li ng-repeat="fruit in model.fruits track by $index">
                   <input ng-model="model.fruits[$index]">
                </li>
            </ul>

            <br/>

        Friends:
            <ul>
                <li ng-repeat="friend in model.friends">
                    Name: <input ng-model="friend.name">
                    Age: <input ng-model="friend.age" type="number"> </li>
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
    wilma = Person(name="Wilma", age=42)
    barney = Person(name="Barney", age=40)

    fred.fruits = ['peach', 'pear']

    def set_list():
        fred.fruits = ["banana", "kiwi"]
        fred.friends = [wilma]

    def update_list():
        fred.fruits.append("apple")
        fred.friends.append(barney)
        fred.fruits[0] = 'mango'

    app = QtGui.QApplication.instance() or QtGui.QApplication([])
    GUI.invoke_after(3000, set_list)
    GUI.invoke_after(4000, update_list)

    person_view.show(model=fred)
    app.exec_()
    print fred.fruits
    print [x.name for x in fred.friends]

if __name__ == "__main__":
    main()
