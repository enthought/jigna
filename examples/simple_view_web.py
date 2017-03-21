"""
This example shows how to serve a simple jigna view over the web.
"""

#### Imports ####
from __future__ import print_function

from tornado.ioloop import IOLoop
from traits.api import HasTraits, Int, Str
from jigna.api import Template, WebApp

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

template = Template(body_html=body_html)

#### Entry point ####

def main():
    # Start the tornado ioloop application
    ioloop = IOLoop.instance()

    # Instantiate the domain model
    fred = Person(name='Fred', age=42)

    # Create a web app serving the view with the domain model added to its
    # context.
    app = WebApp(template=template, context={'person': fred})
    app.listen(8000)

    # Start serving the web app on port 8000.
    #
    # Point your web browser to http://localhost:8000/ to connect to this jigna
    # web app. Any operation performed on the client directly update the
    # model attributes on the server.
    print('Serving on port 8000...')
    ioloop.start()

if __name__ == "__main__":
    main()

#### EOF ######################################################################
