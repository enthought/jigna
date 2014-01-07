""" This example demonstrates a progress bar to show how the UI is not
blocked during a slow method call. This is because the method calls are
performed in a separate thread.
"""

#### Imports ##################################################################

from traits.api import HasTraits, Int, Str
from pyface.qt import QtGui
from jigna.api import View
import time

#### Domain model ####

class Person(HasTraits):
    name = Str
    age  = Int

    power = Int

    def install_new_power(self):
        print "Installing new power...."

        while self.power < 100:
            time.sleep(0.5)
            self.power += 10
            print "Power increased to: ", self.power

        self.name = 'Batman'
        self.age = 400

    def download_new_power(self):
        print "Downloading new power...."
        
        time.sleep(1)
        
        import urllib2
        urllib2.urlopen('http://someboguswebsite.com')

        print "error!"

#### UI layer ####

body_html = """
    <div ng-controller='MainCtrl'>
      Name: <input ng-model="model.name">
      Age: <input ng-model="model.age" type='number'>
      Power: {{model.power}}
      <button id="install_btn" ng-click="install_new_power_async($event)">
        Install new power!
      </button>

      <button id="download_btn" ng-click="download_new_power_async($event)">
        Download new power!
      </button>

      <div class='progress-bar-container'>
        <div class='completed-progress' ng-style="{ width: model.power + '%' }"></div>
      </div>
    </div>

    <script type="text/javascript">
        var app = angular.module('MyApp', ['jigna']);

        app.controller('MainCtrl', function($scope){
            $scope.install_new_power_async = function(event) {
                $scope.model.install_new_power_async()
                .done(function(){
                    $(event.target).html("Installed")
                })
            }

            $scope.download_new_power_async = function(event) {
                $scope.model.download_new_power_async()
                .fail(function(error){
                    $(event.target).html("Error!")
                })
            }
        })

        angular.bootstrap(document, ['MyApp']);
    </script>

    <style type="text/css">
        .progress-bar-container {
            height: 10px;
            border: solid 1px #999;
            background-color: white;
            margin-top: 10px;
        }
        .completed-progress {
            background-color: blue;
            height: 100%;
        }
    </style>
"""

person_view = View(body_html=body_html)

#### Entry point ####

def main():
    bruce = Person(name='Bruce', age=30)
    person_view.show(model=bruce)
    
if __name__ == '__main__':
    app = QtGui.QApplication.instance() or QtGui.QApplication([])
    main()
    app.exec_()

#### EOF ######################################################################
