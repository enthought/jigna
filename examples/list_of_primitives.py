"""
This example shows two-way data binding for the `List` traits whose items are of
the primitive type.
"""

#### Imports ##################################################################

from traits.api import HasTraits, Str, List
from pyface.qt import QtGui
from jigna.api import View

#### Domain model ####

class Basket(HasTraits):
    fruits = List(Str)

#### UI layer ####

# Looping over the list of primitive variables using `ng-repeat`. We need to add
# `track by $index` for primitive variables so that the order of the items in
# the view is bound to the list order in the model.
body_html = """
    <div>
      Fruits in the basket:
      <div ng-repeat="fruit in basket.fruits track by $index">
        <input ng-model="basket.fruits[$index]">
      </div>
    </div>
"""

basket_view = View(body_html=body_html)

#### Entry point ####

def main():
    # Start a QtGui application
    app = QtGui.QApplication([])

    # Instantiate the domain model
    basket = Basket(fruits=['peach', 'pear'])

    # Render the view with the domain model added to the context
    basket_view.show(basket=basket)

    # Schedule some operations on the list
    from pyface.timer.api import do_after
    do_after(2500, basket.fruits.append, 'mango')
    do_after(5000, basket.fruits.insert, 0, 'banana')

    # Start the event loop
    app.exec_()

    # Check the final values of the list attribute
    print basket.fruits

if __name__ == "__main__":
    main()

#### EOF ######################################################################
