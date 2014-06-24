"""
This example shows how to embed a Mayavi QWidget inside the jigna view using
an <object> tag.

Mayavi widget is different than a Chaco widget since you can interact with the
widget so it demonstrates that mouse events are properly forwarded to the
underlying QWidget when you embed it in jigna view.
"""

#### Imports ####

from traits.api import HasTraits, Instance, CInt, on_trait_change
from mayavi.core.api import PipelineBase
from mayavi.core.ui.api import MlabSceneModel
from pyface.qt import QtGui
from jigna.api import View

#### Domain model ####

class SceneController(HasTraits):
    n_meridional    = CInt
    n_longitudinal  = CInt

    scene = Instance(MlabSceneModel, ())

    plot = Instance(PipelineBase)

    # When the scene is activated, or when the parameters are changed, we
    # update the plot.
    @on_trait_change('n_meridional,n_longitudinal,scene.activated')
    def update_plot(self):
        x, y, z, t = self.get_data()
        if self.plot is None:
            self.plot = self.scene.mlab.plot3d(x, y, z, t,
                                tube_radius=0.025, colormap='Spectral')
        else:
            self.plot.mlab_source.set(x=x, y=y, z=z, scalars=t)

    def get_data(self):
        """ Obtain the x,y,z,t data for the domain equation and given values of
        n_meridional and n_longitudinal
        """
        from numpy import arange, pi, cos, sin
        phi = arange(0.0, 2*pi + 0.5*pi/1000, pi/1000, 'd')

        mu = phi*self.n_meridional
        x = cos(mu) * (1 + cos(self.n_longitudinal * mu/self.n_meridional)*0.5)
        y = sin(mu) * (1 + cos(self.n_longitudinal * mu/self.n_meridional)*0.5)
        z = 0.5 * sin(self.n_longitudinal*mu/self.n_meridional)
        t = sin(mu)

        return x, y, z, t

    def create_scene_widget(self):
        """ Factory method to create the QWidget for the Mayavi scene.

        This follows the same approach as the Chaco example i.e. create a hidden
        traitsui view based on the mayavi SceneEditor and return it's 'control'
        to obtain the required QWidget.
        """
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
      N meridonial: <input type="number" ng-model="scene_controller.n_meridional"
                       min=0 max=100><br>
      N longitudinal: <input type="number" ng-model="scene_controller.n_longitudinal"
                       min=0 max=100><br>
      Plot:<br>

      <object type="application/x-qwidget" width="400" height="400"
              widget-factory="scene_controller.create_scene_widget">
      </object>
    </div>
"""

scene_controller_view = View(body_html=body_html)

#### Entry point ####

def main():
    # Start a QtGui application
    app = QtGui.QApplication.instance() or QtGui.QApplication([])

    # Instantiate the domain model
    scene_controller = SceneController()

    # Render the view with the domain model added to the context
    widget = scene_controller_view.create_widget(
        context={'scene_controller': scene_controller}
    )
    widget.show()

    # Start the event loop
    app.exec_()

if __name__ == "__main__":
    main()

#### EOF ######################################################################
