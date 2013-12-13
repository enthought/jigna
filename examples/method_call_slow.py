"""This example demonstrates a progress bar to show how the UI is not
blocked during a slow method call. This is because the method calls are
performed in a separate thread.
"""

#### Imports ##################################################################

from traits.api import HasTraits, Int, Str
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

import time

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

#### UI layer ####

html = """
<html ng-app='MyApp'>
    <head>
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
        
        <script src='/jigna/js/jquery.min.js'></script>
        <script src='/jigna/js/angular.min.js'></script>
        <script src='/jigna/js/jigna.js'></script>

        <script type="text/javascript">
            var app = angular.module('MyApp', ['jigna']);

            app.controller('MainCtrl', function($scope){
                $scope.install_new_power_async = function(event) {
                    $scope.model.install_new_power_async()
                    .done(function(){
                        $(event.target).html("Installed")
                    })
                }
            })
        </script>
    </head>

    <body ng-controller='MainCtrl'>
        <div>
          Name: <input ng-model="model.name">
          Age: <input ng-model="model.age" type='number'>
          Power: {{model.power}}
          <button id="install_btn" ng-click="install_new_power_async($event)">
            Install new power!
          </button>

          <div class='progress-bar-container'>
            <div class='completed-progress' ng-style="{ width: model.power + '%' }"></div>
          </div>

        </div>
    </body>
</html>
"""

person_view = View(html=html)

#### Entry point ####

def main():
    bruce  = Person(name='Bruce', age=30)

    args = parse_command_line_args(description=__doc__)
    if args.web:
        person_view.serve(model=bruce)
    else:
        app = QtGui.QApplication.instance() or QtGui.QApplication([])
        person_view.show(model=bruce)
        app.exec_()

    print bruce.name, bruce.age

    return

if __name__ == '__main__':
    main()

#### EOF ######################################################################
