from traits.api import HasTraits, Int, Str
from jigna.jigna_view import JignaView
from pyface.qt import QtGui
from pyface.api import GUI

#### Domain model ####

class Person(HasTraits):
    name = Str
    age  = Int

#### UI layer ####

html = """
    <div data-model-name="model" ng-controller="Person">
    	Name: <input ng-model="model.name">
    	Age: <input ng-model="model.age" type='number'>
    </div>
"""

person_view = JignaView(html=html)

#### Entry point ###

def main():
	def listener(obj, traitname, old, new):
		print obj, traitname, old, new
		
	fred  = Person(name='Fred', age=42)
	fred.on_trait_change(listener)
	def update_fred():
		fred.name = "Wilma"
		fred.age = 4
	app = QtGui.QApplication.instance() or QtGui.QApplication([])
	GUI.invoke_after(3000, update_fred)
	person_view.show(model=fred)
	app.exec_()
	print fred.name
	print fred.age

if __name__ == "__main__":
	main()
