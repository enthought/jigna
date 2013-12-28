"""
This example is the most basic example which shows two-way data binding
in Jigna. Some traits change automatically after some time on the model
so you should see the corresponding change in the HTML DOM.
"""

#### Imports ##################################################################

from traits.api import HasTraits, Int, Str
from pyface.qt import QtGui
from pyface.timer.api import do_after
from jigna.api import View

#### Domain model ####

class Person(HasTraits):
    name = Str
    age  = Int

    def update_name(self, name):
        self.name = name

#### UI layer ####

body_html = """
    <div>
      Name: <input ng-model="model.name">
      Age: <input ng-model="model.age" type='number'>
    </div>
"""

person_view = View(body_html=body_html)

#### Entry point ####

def main():
    fred  = Person(name='Fred', age=42)
    def on_trait_change(obj, trait, old, new):
        print trait, old, new
    fred.on_trait_change(on_trait_change)
    person_view.show(model=fred)
    do_after(2000, fred.update_name, "Freddie")

if __name__ == "__main__":
    app = QtGui.QApplication.instance() or QtGui.QApplication([])
    main()
    app.exec_()

#### EOF ######################################################################
