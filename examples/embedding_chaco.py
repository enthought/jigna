"""
This example shows how to embed a Chaco QWidget inside the jigna view using
an <object> tag.
"""

#### Imports ####

from traits.api import HasTraits, CInt, Instance
from chaco.api import Plot, ArrayPlotData
from pyface.qt import QtGui
from jigna.api import View

#### Domain model ####

class PlotController(HasTraits):

    # A scaling factor which governs how the plot will look. Whenever the scaling
    # factor changes, we get the data again and update the plot.
    scaling_factor = CInt
    def _scaling_factor_changed(self):
        x, y = self.get_data()
        self.plot.data.set_data('y', y)

    # The Chaco Plot object. This is the object which is usually visualized via
    # traitsui using the enable ComponentEditor
    plot  = Instance(Plot)
    def _plot_default(self):
        x, y = self.get_data()

        plot = Plot(ArrayPlotData(x=x, y=y))
        plot.plot(("x", "y"), type="line", color="blue")

        return plot

    def get_data(self):
        """ Obtain the x,y data for the domain equation and given scaling factor
        """
        from numpy import linspace, sin
        x = linspace(-14, 14, 1000)
        y = sin(self.scaling_factor * x) * x**3

        return x, y

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
        ui = self.edit_traits(view=view, parent=QtGui.QWidget(), kind='subpanel')

        return ui.control


#### UI layer ####

body_html = """
    <div>
      Scaling factor: <input type="range" ng-model="plot_controller.scaling_factor"
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

plot_controller_view = View(body_html=body_html)

#### Entry point ####

def main():
    # Start a QtGui application
    app = QtGui.QApplication.instance() or QtGui.QApplication([])

    # Instantiate the domain model
    plot_controller = PlotController(scaling_factor=0.5)

    # Render the view with the domain model added to the context
    plot_controller_view.show(plot_controller=plot_controller)

    # Start the event loop
    app.exec_()

if __name__ == "__main__":
    main()

#### EOF ######################################################################
