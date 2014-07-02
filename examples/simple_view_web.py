"""
This example shows how to serve a simple jigna view over the web.
"""

#### Imports ####

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
    # Instantiate the domain model
    fred = Person(name='Fred', age=42)

    # Create a web app serving the view with the domain model added to its
    # context.
    app = WebApp(template=template, context={'person': fred}, port=8000)

    # Start serving the web app on port 8000.
    #
    # Point your web browser to http://localhost:8000/ to connect to this jigna
    # web app. Any operation performed on the client directly update the
    # model attributes on the server.
    app.start()

if __name__ == "__main__":
    main()

#### EOF ######################################################################
