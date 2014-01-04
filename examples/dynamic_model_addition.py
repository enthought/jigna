"""
This example shows how a model can be added dynamically to the scope.
"""

#### Imports ####

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
      Model 1:  
      Name: <input ng-model="model1.name">
      Age: <input ng-model="model1.age" type='number'>

      <br><br>

      Model 2: 
      Name: <input ng-model="model2.name">
      Age: <input ng-model="model2.age" type='number'>


    </div>
"""

person_view = View(body_html=body_html)

#### Entry point ####

def add_model():
    wilma = Person(name='Wilma', age=25)
    person_view.update_context(model2=wilma)

def main():
    app = QtGui.QApplication.instance() or QtGui.QApplication([])
    
    fred = Person(name='Fred', age=42)
    person_view.show(model1=fred)
    do_after(2000, add_model)

    app.exec_()

if __name__ == "__main__":
    main()

#### EOF ######################################################################
