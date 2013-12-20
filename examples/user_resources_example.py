"""
This example shows how to add additional resources like CSS/Javascript/ image
files in your html by specifying a base url.
"""

#### Imports ##################################################################

from traits.api import HasTraits, Int, Str
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

body_html = """
    <div>
        Name: <input ng-model="model.name">
              <span class='red'>Always red - {{model.name}}</span>
        Age:  <input ng-model="model.age" type='number'>
              <span class='hoverme'>Hover me: {{model.age}}</span>
        <img src='data/lena.png' />
    </div>
    <script type='text/javascript' src='data/colorchange.js'></script>
    <link rel='stylesheet' href='data/color.css' />
"""

person_view = View(body_html=body_html, base_url='')

#### Entry point ####

def main():
    def listener(obj, traitname, old, new):
        print obj, traitname, old, new

    fred  = Person(name='Fred', age=42)
    fred.on_trait_change(listener)
    def update_fred():
        fred.name = "Wilma"
        fred.age = 4

    args = parse_command_line_args(description=__doc__)
    if args.web:
        import time
        from threading import Thread
        t = Thread(target=lambda:time.sleep(2) or update_fred())
        t.daemon = True
        t.start()
        person_view.serve(model=fred)
    else:
        from pyface.qt import QtGui
        from pyface.timer.api import do_after
        app = QtGui.QApplication.instance() or QtGui.QApplication([])
        person_view.show(model=fred)
        do_after(2000, update_fred)
        app.exec_()
    print fred.name
    print fred.age

if __name__ == "__main__":
    main()

#### EOF ######################################################################
