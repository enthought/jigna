from traits.api import HasTraits, Int, Str
from jigna.api import JignaView
from pyface.qt import QtGui
from pyface.timer.api import do_after

#### Domain model ####

class Person(HasTraits):
    name = Str
    age  = Int

#### UI layer ####

html = """
    <html ng-app>
        <head>
            <script src='http://resources.jigna/js/jquery.min.js'></script>
            <script src='http://resources.jigna/js/angular.min.js'></script>
            <script src='http://resources.jigna/js/jigna.js'></script>
        </head>

        <body>
            Name: <input ng-model="model.name">
            Age: <input ng-model="model.age" type='number'>
        </body>
    </html>
"""

person_view = JignaView(html=html)

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
