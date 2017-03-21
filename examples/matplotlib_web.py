#### Imports ####
from __future__ import print_function

from jigna.api import Template, WebApp
from numpy import linspace, sin, pi
from tornado.ioloop import IOLoop
from traits.api import (
    HasTraits, CInt, Str, Property, Array, Instance, on_trait_change
)

#### Domain model ####

class DomainModel(HasTraits):
    """
    The algorithmic domain model which specifies the mathematical relationship
    between x and y.
    """

    #: Independent variable of the domain equation
    x = Array
    def _x_default(self):
        return linspace(-2*pi, 2*pi, 200)

    #: Dependent variable of the domain equation
    y = Property(Array, depends_on=['x', 'scaling_factor'])
    def _get_y(self):
        return sin(self.scaling_factor * self.x) / self.x

    #: A scaling factor to tune the output
    scaling_factor = CInt

#### Controller layer ####

class PlotController(HasTraits):
    """
    A Controller class which creates a matplotlib plot object (in the form of a
    png image bytestream) for the given domain model.
    """

    #: Instance of the domain model which is being displayed by this controller
    domain_model = Instance(DomainModel)

    #: The 'png' bytestream representation of the matplotlib plot object
    plot = Str

    @on_trait_change('domain_model.scaling_factor')
    def update_plot(self):
        # Use the Agg backend to generate images without making the window appear
        import matplotlib
        matplotlib.use('Agg')

        # Generate the plot
        from matplotlib import pyplot
        pyplot.clf()
        pyplot.plot(self.domain_model.x, self.domain_model.y)

        # Generate image data in png format
        from io import StringIO
        stream = StringIO()
        pyplot.savefig(stream, format='png')
        stream.seek(0)
        self.plot = stream.buf.encode('base64')

#### UI layer ####

body_html = """
   <div>
        Scaling factor: <input type="range" ng-model="domain_model.scaling_factor"
                        min=0 max=30><br>
        Plot:<br>
        <img ng-src="data:image/png;base64,{{plot_controller.plot}}">
    </div>
"""

template = Template(body_html=body_html)

#### Entry point ####

def main():
    # Start the tornado ioloop application
    ioloop = IOLoop.instance()

    # Instantiate the domain model and the plot controller
    domain_model = DomainModel(scaling_factor=15)
    plot_controller = PlotController(domain_model=domain_model)

    # Create a WebApp to render the HTML template with the given context.
    #
    # The web app shows a matplotlib plot in a browser by displaying the png
    # image of the plot. Moving the HTML slider on the UI changes the domain
    # model and hence the plot image.
    app = WebApp(
        template=template,
        context={
            'domain_model': domain_model,
            'plot_controller': plot_controller
        }
    )
    app.listen(8000)

    # Start serving the web app on port 8000.
    print('Serving on port 8000...')
    ioloop.start()

if __name__ == "__main__":
    main()

#### EOF ######################################################################
