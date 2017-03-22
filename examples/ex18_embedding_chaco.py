"""
This example shows how to embed a Chaco QWidget inside the jigna view using
an <object> tag.
"""

#### Imports ####

from chaco.api import Plot, ArrayPlotData
from jigna.api import HTMLWidget, Template
from jigna.qt import QtGui
from numpy import linspace, sin
from traits.api import (
    HasTraits, CInt, Instance, Array, Property, on_trait_change
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
        return linspace(-14, 14, 1000)

    #: Dependent variable of the domain equation
    y = Property(Array, depends_on=['x', 'scaling_factor'])
    def _get_y(self):
        return sin(self.scaling_factor * self.x) * self.x**3

    #: A scaling factor to tune the output
    scaling_factor = CInt

#### Controller layer ####

class PlotController(HasTraits):
    """
    A Controller class which creates a Chaco plot object for the given domain
    model.
    """

    #: Instance of the domain model which is being displayed by this controller
    domain_model = Instance(DomainModel)

    # The Chaco Plot object. This is the object which is usually visualized via
    # traitsui using the enable ComponentEditor
    plot  = Instance(Plot)
    def _plot_default(self):
        plot = Plot(ArrayPlotData(x=self.domain_model.x, y=self.domain_model.y))
        plot.plot(("x", "y"), type="line", color="blue")

        return plot

    @on_trait_change('domain_model.scaling_factor')
    def update_plot(self):
        self.plot.data.set_data('x', self.domain_model.x)
        self.plot.data.set_data('y', self.domain_model.y)

    def create_plot_widget(self):
        """ This method is used as a factory to create the QWidget for the Chaco
        'plot' component.

        This is the standard way to obtain the QWidget out of a Chaco Plot object.
        We create a hidden traitsui view and return it's 'control' to obtain the
        required QWidget.
        """
        from traitsui.api import View, Item
        from enable.api import ComponentEditor

        view = View(Item('plot', editor=ComponentEditor(), show_label=False))
        ui = self.edit_traits(view=view, parent=None, kind='subpanel')

        return ui.control

#### UI layer ####

body_html = """
    <div>
      Scaling factor: <input type="range" ng-model="domain_model.scaling_factor"
                       min=0 max=100><br>
      Plot:<br>

      <!-- Specify type='application/x-qwidget' to embed a QWidget in the jigna
      view. Note that 'widget-factory' here refers to the factory method in
      Python which will generate that QWidget. -->
      <div>
        <object type="application/x-qwidget"
                widget-factory="plot_controller.create_plot_widget"
                width="500" height="400">
        </object>
      </div>
    </div>
"""

template = Template(body_html=body_html, recommended_size=(600, 600))

#### Entry point ####

def main():
    # Start the Qt application
    app = QtGui.QApplication.instance() or QtGui.QApplication([])

    # Instantiate the domain model and the plot controller
    domain_model = DomainModel(scaling_factor=50)
    plot_controller = PlotController(domain_model=domain_model)

    # Create the jigna based HTML widget which renders the given HTML template
    # with the given context.
    #
    # The widget contains an embedded Chaco QWidget showing a 2D plot of
    # the domain model. Moving the slider on the UI changes the domain model
    # and hence the Chaco plot.
    widget = HTMLWidget(
        template=template,
        context={
            'domain_model': domain_model,
            'plot_controller': plot_controller
        }
    )
    widget.show()

    # Start the event loop
    app.exec_()

if __name__ == "__main__":
    main()

#### EOF ######################################################################
