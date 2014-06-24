"""
This example shows how to serve a simple jigna view over the web.
"""

#### Imports ####

from traits.api import HasTraits, Int, Str
from jigna.api import View
from tornado.ioloop import IOLoop

#### Domain model ####

class Person(HasTraits):
    name = Str
    age  = Int

#### UI layer ####

body_html = """
    <div>
      Name: <input ng-model="person.name"><br>
      Age: <input ng-model="person.age" type='number'>
    </div>
"""

person_view = View(body_html=body_html)

#### Entry point ####

def main():
    # Start the tornado ioloop
    ioloop = IOLoop.instance()

    # Instantiate the domain model
    fred = Person(name='Fred', age=42)

    # Start serving the view with the domain model added to the context. This
    # will start the tornado ioloop.
    #
    # Point your web browser to http://localhost:8888/ to connect to the jigna
    # view. Any operation performed on the view there directly update the model
    # attributes here.
    person_view.create_webapp(8888, context={'person': fred})

    # Start the event loop
    ioloop.start()

if __name__ == "__main__":
    main()

#### EOF ######################################################################
