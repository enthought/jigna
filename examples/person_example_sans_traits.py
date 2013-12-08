""" This example shows the ability to view generic Python objects (not just
HasTraits objects) in HTML using Jigna. The data binding will only be one-way
in this case, i.e. from the UI to the model.
"""

#### Imports ##################################################################

from pyface.qt import QtGui
from jigna.api import View

#### Utility function    ######################################################
def parse_command_line_args(argv=None, description="Example"):
    import argparse
    parser = argparse.ArgumentParser(
        description=description,
        add_help=True
        )
    parser.add_argument("--web",
                        help="Run the websocket version by starting a tornado server\
                        on port 8888",
                        action="store_true")
    args = parser.parse_args(argv)
    return args


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

    fred  = Person(name='Fred', age=42)
    args = parse_command_line_args(description=__doc__)
    if args.web:
        def dump_status():
            print fred.name, fred.age
        import time
        from threading import Thread
        t = Thread(target=lambda:time.sleep(5) or dump_status())
        t.daemon = True
        t.start()
        person_view.serve(model=fred)
    else:
        app = QtGui.QApplication.instance() or QtGui.QApplication([])
        person_view.show(model=fred)
        app.exec_()

    print fred.name
    print fred.age

if __name__ == "__main__":
    main()

#### EOF ######################################################################
