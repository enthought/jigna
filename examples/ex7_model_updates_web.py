"""
This example demonstrates how to schedule updates to the application model in
the web version.
"""

#### Imports ####
from __future__ import print_function

import datetime
from jigna.web_app import WebApp
from jigna.template import Template
from tornado.ioloop import IOLoop
from traits.api import HasTraits, Str

#### Domain model ####

class MOTD(HasTraits):
    message = Str

    def update_message(self, message):
        self.message = message

#### UI layer ####

body_html = """
    <div>
      Message of the day: {{motd.message}}
    </div>
"""

template = Template(body_html=body_html)

#### Entry point ####

def main():
    # Obtain the tornado ioloop object
    ioloop = IOLoop.instance()

    # Instantiate the domain model
    motd = MOTD(message="Explicit is better than implicit.")

    # Create a web app serving the view with the domain model added to its
    # context.
    app = WebApp(template=template, context={'motd':motd})
    app.listen(8000)

    # Schedule an update to a model variable after 10 seconds. If the user's
    # browser is connected to the web app before 10 seconds, it will see the
    # change in the model variable happening. Otherwise, it will only see the
    # updated value.
    #
    # NOTE: The way to schedule a task in the future has been greatly improved
    # in Tornado 4.1.dev version. You can specify additional arguments to
    # methods etc.
    delay = datetime.timedelta(0, 10)
    ioloop.add_timeout(delay,
        lambda : motd.update_message("Flat is better than nested.")
    )

    # Start serving the web app on port 8000.
    print('Serving on port 8000...')
    ioloop.start()

if __name__ == "__main__":
    main()

#### EOF ######################################################################
