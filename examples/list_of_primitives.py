"""
This example shows two-way data binding for the `List` traits whose items are of
the primitive type.
"""

#### Imports ####
from __future__ import print_function

from traits.api import HasTraits, Str, List
from jigna.api import HTMLWidget, Template
from jigna.qt import QtGui
from jigna.utils.gui import do_after

#### Domain model ####

class Basket(HasTraits):
    fruits = List(Str)

#### UI layer ####

# Looping over the list of primitive variables using `ng-repeat` has two gotchas
# (both of them are standard AngularJS gotchas):
#
# 1. We need to add `track by $index` for looping through primitive variables
# otherwise angular creates new DOM nodes for every edit of the variable. One
# manifestation of this behaviour is that the input field gets out of focus for
# every edit since each edit really creates a new input field node.
# See http://www.bennadel.com/blog/2556-using-track-by-with-ngrepeat-in-angularjs-1-2.htm
#
# 2. We can't write to the `fruit` variable by making a local assignment i.e.
# `ng-model="fruit"`. This is because `fruit` refers to a local scope variable,
# so any writes to this local variable won't update the model values in Python
# which are bound to the $rootScope.
# See http://stackoverflow.com/questions/15488342/binding-inputs-to-an-array-of-primitives-using-ngrepeat-uneditable-inputs

body_html = """
    <div>
      Fruits in the basket:
      <div ng-repeat="fruit in basket.fruits track by $index">
        <input ng-model="basket.fruits[$index]">
      </div>
    </div>
"""

template = Template(body_html=body_html)

#### Entry point ####

def main():
    # Start the Qt application
    app = QtGui.QApplication([])

    # Instantiate the domain model
    basket = Basket(fruits=['peach', 'pear'])

    # Create the jigna based HTML widget which renders the given HTML template
    # with the given context.
    widget = HTMLWidget(template=template, context={'basket':basket})
    widget.show()

    # Schedule some operations on the list.
    #
    # We're trying to append and insert primitives to the list in the future.
    # This should be reflected in the UI.
    do_after(2500, basket.fruits.append, 'mango')
    do_after(5000, basket.fruits.insert, 0, 'banana')

    # Start the event loop
    app.exec_()

    # Check the final values of the list attribute
    print(basket.fruits)

if __name__ == "__main__":
    main()

#### EOF ######################################################################
