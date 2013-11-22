#### Example description ######################################################

import argparse
parser = argparse.ArgumentParser(
    description="""
        This example shows how to initialize Jigna's HTML interface by reading 
        a full html file, rather than specifying body_html and head_html.
    """, 
    add_help=True
    )
parser.add_argument("--web", 
                    help="Run the websocket version by starting a tornado server\
                     on port 8888", 
                    action="store_true")
args = parser.parse_args()

#### Imports ##################################################################

from os.path import join
from traits.api import HasTraits, Int, Str
from pyface.qt import QtGui
from pyface.timer.api import do_after
if args.web == True:
    from jigna.api import WebSocketView as View
else:
    from jigna.api import View

#### Domain model ####

class Person(HasTraits):
    name = Str
    age  = Int

#### UI layer ####

person_view = View.from_file(html_file=join('data', 'test.html'))

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
