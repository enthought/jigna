#### Example description ######################################################

import argparse
parser = argparse.ArgumentParser(
    description="""
        This example is the most basic example which shows two-way data binding 
        in Jigna. Some traits change automatically after some time on the model
        so you should see the corresponding change in the HTML DOM.
    """, 
    add_help=True
)
parser.add_argument("--web", 
                    help="Run the websocket version by starting a tornado server\
                     on port 8888", 
                    action="store_true")
args = parser.parse_args()

#### Imports ##################################################################

from traits.api import HasTraits, Int, Str
from pyface.qt import QtGui
from pyface.timer.api import do_after
from jigna.api import View


#### Domain model ####

class Person(HasTraits):
    name = Str
    age  = Int

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
    def listener(obj, traitname, old, new):
        print obj, traitname, old, new

    fred  = Person(name='Fred', age=42)
    fred.on_trait_change(listener)
    def update_fred():
        fred.name = "Wilma"
        fred.age = 4

    app = QtGui.QApplication.instance() or QtGui.QApplication([])
    if args.web:
      from threading import Thread
      t = Thread(target=person_view.serve, kwargs=dict(model=fred))
      t.daemon = True
      t.start()
    else:
        person_view.show(model=fred)
    do_after(2000, update_fred)
    app.exec_()
    print fred.name
    print fred.age

if __name__ == "__main__":
    main()

#### EOF ######################################################################
