#### Example description ######################################################

import argparse
parser = argparse.ArgumentParser(
    description="""
        This example shows the ability to view generic Python objects (not just
        HasTraits objects) in HTML using Jigna. The data binding will only be 
        one-way in this case, i.e. from the UI to the model. 
    """, 
    add_help=True
    )
parser.add_argument("--web", 
                    help="Run the websocket version by starting a tornado server\
                     on port 8888", 
                    action="store_true")
args = parser.parse_args()

#### Imports ##################################################################

from pyface.qt import QtGui
if args.web == True:
    from jigna.api import WebSocketView as View
else:
    from jigna.api import View

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
