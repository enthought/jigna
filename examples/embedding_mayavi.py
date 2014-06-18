"""
This example shows how to embed a Mayavi QWidget inside Jigna web page using
the object tag.
"""

#### Imports ##################################################################

from numpy import arange, pi, cos, sin

from traits.api import HasTraits, Range, Instance, on_trait_change

from mayavi.core.api import PipelineBase
from mayavi.core.ui.api import MlabSceneModel
from pyface.qt import QtGui
from jigna.api import View


dphi = pi/1000.
phi = arange(0.0, 2*pi + 0.5*dphi, dphi, 'd')

def curve(n_mer, n_long):
    mu = phi*n_mer
    x = cos(mu) * (1 + cos(n_long * mu/n_mer)*0.5)
    y = sin(mu) * (1 + cos(n_long * mu/n_mer)*0.5)
    z = 0.5 * sin(n_long*mu/n_mer)
    t = sin(mu)
    return x, y, z, t

class MyModel(HasTraits):
    n_meridional    = Range(0, 30, 6, )
    n_longitudinal  = Range(0, 30, 11, )

    scene = Instance(MlabSceneModel, ())

    plot = Instance(PipelineBase)

    # When the scene is activated, or when the parameters are changed, we
    # update the plot.
    @on_trait_change('n_meridional,n_longitudinal,scene.activated')
    def update_plot(self):
        x, y, z, t = curve(self.n_meridional, self.n_longitudinal)
        if self.plot is None:
            self.plot = self.scene.mlab.plot3d(x, y, z, t,
                                tube_radius=0.025, colormap='Spectral')
        else:
            self.plot.mlab_source.set(x=x, y=y, z=z, scalars=t)

    def create_plot_widget(self):
        from traitsui.api import View, Item
        from mayavi.core.ui.api import MayaviScene, SceneEditor
        view = View(Item('scene', show_label=False,
                         editor=SceneEditor(scene_class=MayaviScene)),
                         resizable=True)
        ui = self.edit_traits(view=view, parent=QtGui.QWidget(), kind='subpanel')

        return ui.control


#### UI layer ####

body_html = """
    <div>
      N meridonial: <input type="number" ng-model="model.n_meridional"
                       min=0 max=100><br>
      N longitudinal: <input type="number" ng-model="model.n_longitudinal"
                       min=0 max=100><br>
      Plot:<br>

      <object type="application/x-qwidget" width="400" height="400"
              widget-factory="model.create_plot_widget">
      </object>
    </div>
"""

plot_view = View(body_html=body_html)

#### Entry point ####

def main():
    plot  = MyModel()
    plot_view.show(model=plot)

if __name__ == "__main__":
    app = QtGui.QApplication.instance() or QtGui.QApplication([])
    main()
    app.exec_()

#### EOF ######################################################################
