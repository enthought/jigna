from jigna.api import View
from pyface.qt import QtGui

#### Domain model ####

class Person(object):
    def __init__(self, name, age):
        self.name = name
        self.age = age

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

    app = QtGui.QApplication.instance() or QtGui.QApplication([])

    fred  = Person(name='Fred', age=42)
    person_view.show(model=fred)

    app.exec_()

    print fred.name
    print fred.age

if __name__ == "__main__":
    main()

#### EOF ######################################################################
