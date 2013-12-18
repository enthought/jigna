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

class Person(HasTraits):
    name = Str
    age  = Int

#### UI layer ####

person_view = View(html_file=join('data', 'test.html'))

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
    args = parse_command_line_args(description=__doc__)
    if args.web:
        from threading import Thread
        t = Thread(target=person_view.serve, kwargs=dict(fred=fred, wilma=wilma))
        t.daemon = True
        t.start()
    else:
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
