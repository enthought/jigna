from traits.api import HasTraits, Instance, on_trait_change, Range, Float
from traitsui.api import View, Item, Group, RangeEditor
from chaco.api import Plot, ArrayPlotData
from chaco.tools.api import ZoomTool, PanTool
from enable.api import ComponentEditor
from numpy import sin, cos, linspace
from jigna.html_view import HTMLView
from jigna.session import show_simple_view

class LinePlot(HasTraits):
    scaling_factor = Range(0, 100)

    plot = Instance(Plot)
    plot2 = Instance(Plot)

    traits_view = View(Item('scaling_factor'),
                       Item('plot', editor=ComponentEditor(), show_label=False),
                       Item('plot2', editor=ComponentEditor(), show_label=False),

                       width=500, height=500, resizable=True, title="Chaco Plot")

    def __init__(self, **traits):
        super(LinePlot, self).__init__(**traits)
        self._update_plot()

    @on_trait_change('scaling_factor')
    def _update_plot(self):
        x = linspace(-14, 14, 1000)
        y = sin(self.scaling_factor * x) * x**3
        y1 = cos(self.scaling_factor * x) * x**3
        if self.plot is None:
            plotdata = ArrayPlotData(x=x, y=y, y1=y1)
            plot = Plot(plotdata)
            plot.plot(("x", "y"), type="line", color="blue")
            plot.title = "sin(%s * x) * x^3" % self.scaling_factor
            plot.tools.append(ZoomTool(component=plot))
            plot.tools.append(PanTool(component=plot))
            self.plot = plot
            plot2 = Plot(plotdata)
            plot2.plot(("x", "y1"), type="line", color="red")
            self.plot2 = plot2
            plot2.tools.append(ZoomTool(component=plot2))
            plot2.tools.append(PanTool(component=plot2))
        else:
            self.plot.data.set_data('y', y)
            self.plot.data.set_data('y1', y1)
            self.plot.title = "sin(%s * x) * x^3" % self.scaling_factor

line_plot = LinePlot()
ui = line_plot.edit_traits()

layout = View(Group(Item('scaling_factor', editor=RangeEditor()),
                    Item('plot', editor=ComponentEditor()),
                    Item('plot2', editor=ComponentEditor())
                    ))

view = HTMLView(model=line_plot, layout=layout)
show_simple_view(view)
