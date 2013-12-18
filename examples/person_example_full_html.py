"""
This example shows how to initialize Jigna's HTML interface by reading
a full html file, rather than specifying body_html and head_html.
"""

#### Imports ##################################################################

from os.path import join
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

person_view = View(html_file=join('data', 'test.html'))

#### Entry point ####

def main():
    app = QtGui.QApplication.instance() or QtGui.QApplication([])

    fred  = Person(name='Fred', age=42)
    wilma = Person(name='Wilma', age=25)

    person_view.show(fred=fred, wilma=wilma)

    do_after(2000, fred.update_name, "Freddie")
    do_after(3000, wilma.update_name, "Mrs. Wilma")

    app.exec_()
    
if __name__ == "__main__":
    main()
    

#### EOF ######################################################################
