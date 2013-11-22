#### Example description ######################################################

import argparse
parser = argparse.ArgumentParser(
    description="""
        This example demonstrates Jigna's ability to call public methods of the
        traits model from the HTML interface. You can supply primitive arguments 
        and also pass model variables.
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
if args.web == True:
    from jigna.api import WebSocketView as View
else:
    from jigna.api import View

#### Domain model ####

class Person(HasTraits):
    name = Str
    age  = Int

    def do_something(self):
        print 'do something!!!!!!!!'

    def upper(self, name):
        self.name = name.upper()
        print 'upper', self.name

    def pass_instance(self, obj):
        print 'got obj', obj.name

#### UI layer ####

body_html = """
    <div>
      Name: <input ng-model="model.name">
      Age: <input ng-model="model.age" type='number'>
      <button ng-click="model.do_something()">Do Something!</button>
      <button ng-click="model.upper(model.name)">Upper</button>
      <button ng-click="model.pass_instance(model)">Pass Instance</button>
    </div>
"""

person_view = View(body_html=body_html)

#### Entry point ####

def main():
    fred  = Person(name='Fred', age=42)

    app = QtGui.QApplication.instance() or QtGui.QApplication([])
    person_view.show(model=fred)

    app.exec_()

    return

if __name__ == '__main__':
    main()

#### EOF ######################################################################
