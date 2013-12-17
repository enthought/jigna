"""
This example demonstrates Jigna's ability to respond to traits Event updates.
"""

#### Imports ##################################################################

from traits.api import HasTraits, Int, Str, Event
from pyface.qt import QtGui
from jigna.api import View

import time

#### Domain model ####

class Person(HasTraits):
    name = Str
    age  = Int(25)

    retired = Event

    def grow_old(self, max_age=100):
        while self.age < max_age:
            time.sleep(0.1)
            self.age += 1
            print "Age increased to:", self.age
            if self.age == 60:
                self.retired = True

#### UI layer ####

html = """
<html ng-app='MyApp'>
    <head>
        <script src='/jigna/js/jquery.min.js'></script>
        <script src='/jigna/js/angular.min.js'></script>
        <script src='/jigna/js/jigna.js'></script>
        <script>
            
            var app = angular.module('MyApp', ['jigna']);

            app.controller('MainCtrl', function($scope){
                jigna.event_target.addListener('object_changed', function(evt){
                    if (evt.attribute_name == 'retired') {
                        proxy = jigna.client.get_proxy(evt.obj);
                        proxy['retired'] = 'Yes';
                    }
                })
            })

        </script>
    </head>
    <body ng-controller='MainCtrl'>
         Name: {{model.name}}<br>
         Age:  {{model.age}}

         <button ng-click="model.grow_old_async()">Grow old</button><br>

         Retired?: {{model.retired || 'No'}}
    </body>
</html>
"""

person_view = View(html=html)

#### Entry point ####

def main():
    fred = Person(name='Fred')
    app = QtGui.QApplication.instance() or QtGui.QApplication([])
    person_view.show(model=fred)
    app.exec_()

if __name__ == "__main__":
    main()

#### EOF ######################################################################
