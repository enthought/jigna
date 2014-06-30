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
    # Create the tornado ioloop object
    ioloop = IOLoop.instance()

    # Instantiate the domain model
    fred = Person(name='Fred', age=42)

    # Create a web app serving the view with the domain model added to its
    # context. Start listening on port 8000.
    #
    # Point your web browser to http://localhost:8000/ to connect to the jigna
    # web app. Any operation performed on the view there directly update the
    # model attributes here.
    application = person_view.create_webapp(context={'person': fred})
    application.listen(8000)

    # Start the tornado ioloop
    ioloop.start()

if __name__ == "__main__":
    main()

#### EOF ######################################################################
