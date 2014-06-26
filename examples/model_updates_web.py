"""
This example demonstrates how to schedule updates to the application model in
the web version.
"""

#### Imports ####

from traits.api import HasTraits, Str
from tornado.ioloop import IOLoop
from jigna.api import View

#### Domain model ####

class MOTD(HasTraits):
    message = Str

    def update_message(self):
        self.message = "Flat is better than nested."

#### UI layer ####

body_html = """
    <div>
      Message of the day: {{motd.message}}
    </div>
"""

motd_view = View(body_html=body_html)

#### Entry point ####

def main():
    # Start a tornado application
    ioloop = IOLoop.instance()

    # Instantiate the domain model
    motd = MOTD(message="Explicit is better than implicit.")

    # Render the view with the domain model added to the context
    application = motd_view.create_webapp(context={'motd':motd})
    application.listen(8000)

    # Schedule an update to a model variable
    import datetime
    delay = datetime.timedelta(0, 20)
    ioloop.add_timeout(delay, motd.update_message)

    # Start the event loop
    ioloop.start()

if __name__ == "__main__":
    main()

#### EOF ######################################################################
