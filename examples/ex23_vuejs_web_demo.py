"""
This example shows how to use Jigna using the Vue.js Javascript framework,
instead of AngularJS.
"""

#### Imports ####
from __future__ import print_function

from traits.api import HasTraits, Int, Str, List, Instance
from jigna.vue_template import  VueTemplate
from jigna.web_app import WebApp
from tornado.ioloop import IOLoop


#### Domain model ####

class Person(HasTraits):
    name = Str
    age  = Int
    fruits = List(Str)
    friends = List(Instance('Person'))

    def add_fruit(self, name='fruit'):
        self.fruits.append(name)

    def remove_fruit(self, index):
        del self.fruits[index]

    def update_name(self, name):
        print("Name updated to", name)
        self.name = name

    def add_friend(self):
        self.friends.append(Person(name='Person', age=0))

    def remove_friend(self, index):
        del self.friends[index]

    def _fruits_items_changed(self, l_event):
        print(l_event.added, l_event.removed, l_event.index)

    def _name_changed(self, old, new):
        print("name", old, new)

    def _age_changed(self, old, new):
        print("age", old, new)


#### Entry point ####

def main():
    # Start the tornado ioloop application
    ioloop = IOLoop.instance()

    # Instantiate the domain model

    fred = Person(name='Fred', age=42, fruits=['pear', 'apple'])
    template = VueTemplate(html_file='ex22_vuejs_demo.html')

    # Create the jigna based HTML widget which renders the given HTML template
    # with the given context.
    app = WebApp(template=template, context={'person': fred})
    app.listen(8000)

    # Schedule an update to a model variable after 5 seconds. This update
    # will be reflected in the UI immediately.
    ioloop.call_later(5, setattr, fred, 'update_name', 'Guido')
    ioloop.call_later(5, fred.add_fruit)
    ioloop.call_later(5, fred.add_friend)

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
