from traits.api import HasTraits, Int, Str
from jigna.api import JignaView
from pyface.qt import QtGui
from pyface.timer.api import do_after

#### Domain model ####

class Person(HasTraits):
    name = Str
    age  = Int

#### UI layer ####

head_html = """
      <script type='text/javascript' src='data/colorchange.js'></script>
      <link rel='stylesheet' href='data/color.css' />
"""

body_html = """
    <div>
        Name: <input ng-model="model.name"> 
              <span class='red'>Always red - {{model.name}}</span>
        Age:  <input ng-model="model.age" type='number'>
              <span class='hoverme'>Hover me: {{model.age}}</span>
        <img src='data/lena.png' />
      </div>
"""

person_view = JignaView(body_html=body_html, head_html=head_html, base_url='')

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
