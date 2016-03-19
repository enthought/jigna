"""
This example shows how to serve a simple jigna view over the web.
"""

#### Imports ####
from threading import Thread
from tornado.ioloop import IOLoop
from traits.api import HasTraits, Int, Str
from jigna.template import Template
from jigna.web_app import WebApp
from jigna.utils.web import get_free_port

from selenium import webdriver

#### Domain model ####

class Person(HasTraits):
    name = Str
    age  = Int

    def birthday(self):
        print "HAPPY BDAY"
        self.age += 1

#### UI layer ####

body_html = """
    <div>
      Name: <input ng-model="person.name"><br>
      Age: <input ng-model="person.age" type='number'>
      <button id="birthday" ng-click="jigna.threaded(person, 'birthday')">
      Happy Birthday!
      </button>

     <script>
      // Trigger a threaded call that shows the bug with a dependence on Qt.
      jigna.ready.done(function() {
          setTimeout(function(){$('#birthday').trigger('click');});
      });
     </script>
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
    port = get_free_port()
    app.listen(port)

    t = Thread(target=ioloop.start)
    t.start()
    browser = webdriver.Firefox()
    browser.get('http://localhost:%d'%port)
    import time; time.sleep(1)
    browser.quit()
    ioloop.instance().stop()
    t.join()
    assert fred.age == 43

if __name__ == "__main__":
    main()

#### EOF ######################################################################
