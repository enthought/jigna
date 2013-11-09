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
            <script src='/jigna/js/jquery.min.js'></script>
            <script src='/jigna/js/angular.min.js'></script>
            <script src='/jigna/js/jigna.js'></script>
        </head>

        <body>
            Name: <input ng-model="fred.name">
            Age: <input ng-model="fred.age" type='number'>

            Name: <input ng-model="wilma.name">
            Age: <input ng-model="wilma.age" type='number'>
        </body>
    </html>
"""

person_view = JignaView(html=html)

#### Entry point ####

def main():
    def listener(obj, traitname, old, new):
        print obj, traitname, old, new

    fred  = Person(name='Fred', age=42)
    wilma = Person(name='Wilma', age=4)
    
    fred.on_trait_change(listener)
    def update_fred():
        fred.name = "Freddie"
        fred.age = 43

    def update_wilma():
        wilma.name = "Mrs. Wilma"
        wilma.age = 25

    app = QtGui.QApplication.instance() or QtGui.QApplication([])
    person_view.show(fred=fred, wilma=wilma)
    do_after(2000, update_fred)
    do_after(3000, update_wilma)
    app.exec_()
    print fred.name
    print fred.age
    print wilma.name
    print wilma.age

if __name__ == "__main__":
    main()

#### EOF ######################################################################
