"""
This example shows how to embed a generic QWidget inside Jigna web page using 
the object tag.
"""

#### Imports ##################################################################

from traits.api import HasTraits, CInt, Instance, on_trait_change
from chaco.api import Plot, ArrayPlotData
from chaco.tools.api import ZoomTool, PanTool
from numpy import linspace, sin
from pyface.qt import QtGui
from jigna.api import View

#### Domain model ####

class LinePlot(HasTraits):
    scaling_factor = CInt
    
    plot  = Instance(Plot)
    def _plot_default(self):
        x = linspace(-14, 14, 1000)
        y = sin(self.scaling_factor * x) * x**3

        plot = Plot(ArrayPlotData(x=x, y=y))
        plot.plot(("x", "y"), type="line", color="blue")
        plot.title = "sin(%s * x) * x^3" % self.scaling_factor
        plot.tools.append(ZoomTool(component=plot))
        plot.tools.append(PanTool(component=plot))

        return plot

    @on_trait_change('scaling_factor')
    def update_plot(self):
        x = linspace(-14, 14, 1000)
        y = sin(self.scaling_factor * x) * x**3
        self.plot.data.set_data('y', y)
        self.plot.title = "sin(%s * x) * x^3" % self.scaling_factor

    def create_plot_widget(self):
        from traitsui.api import View, Item
        from enable.api import ComponentEditor

        view = View(Item('plot', editor=ComponentEditor()))
        ui = self.edit_traits(view=view, parent=QtGui.QWidget(), kind='subpanel')

        return ui.control


#### UI layer ####

body_html = """
    <div>
      Scaling factor: <input type="range" ng-model="model.scaling_factor" 
                       min=0 max=100><br>
      Plot:<br>

      <object type="application/x-qwidget"
              widget-factory="model.create_plot_widget">
      </object>
    </div>
"""

plot_view = View(body_html=body_html)

#### Entry point ####

def main():
    line_plot  = LinePlot(scaling_factor=50)
    plot_view.show(model=line_plot)

if __name__ == "__main__":
    app = QtGui.QApplication.instance() or QtGui.QApplication([])
    main()
    app.exec_()

#### EOF ######################################################################
