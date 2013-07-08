from traits.api import HasTraits, Instance, on_trait_change, Range, Float
from traitsui.api import View, Item, Group
from chaco.api import Plot, ArrayPlotData
from chaco.tools.api import ZoomTool, PanTool
from enable.api import ComponentEditor
from numpy import sin, linspace
from jigna.html_view import HTMLView
from jigna.session import show_simple_view
from jigna.editor_factories import _TU_ChacoPlotEditor, _TU_RangeEditor

class LinePlot(HasTraits):
    scaling_factor = Range(0, 100)

    plot = Instance(Plot)

    traits_view = View(Item('scaling_factor'),
                       Item('plot', editor=ComponentEditor(), show_label=False),
                       width=500, height=500, resizable=True, title="Chaco Plot")

    def __init__(self, **traits):
        super(LinePlot, self).__init__(**traits)
        self._update_plot()

    @on_trait_change('scaling_factor')
    def _update_plot(self):
        x = linspace(-14, 14, 1000)
        y = sin(self.scaling_factor * x) * x**3
        if self.plot is None:
            plotdata = ArrayPlotData(x=x, y=y)
            plot = Plot(plotdata)
            plot.plot(("x", "y"), type="line", color="blue")
            plot.title = "sin(%s * x) * x^3" % self.scaling_factor
            plot.tools.append(ZoomTool(component=plot))
            plot.tools.append(PanTool(component=plot))
            self.plot = plot
        else:
            self.plot.data.set_data('y', y)
            self.plot.title = "sin(%s * x) * x^3" % self.scaling_factor

line_plot = LinePlot()
ui = line_plot.edit_traits()

layout = View(Group(Item('scaling_factor', editor=_TU_RangeEditor()),
                    Item('plot', editor=_TU_ChacoPlotEditor())))

view = HTMLView(model=line_plot, layout=layout)
show_simple_view(view)
