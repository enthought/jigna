""" This example shows how to show mayavi in the web version using the webGL
backend for VTK.
"""

#### Imports ####

import json
import tempfile
import numpy as np
from mayavi import mlab
from mayavi.core.api import PipelineBase, ModuleManager
from traits.api import HasTraits, Instance, Int, Str, Property
from tvtk.api import tvtk
from jigna.api import Template, WebApp

mlab.options.offscreen = True
mlab.options.backend = 'test'

#### Domain Model ####

class MeshData(HasTraits):

    dataset = Instance(tvtk.PolyData)

    module_manager = Instance(ModuleManager)

    # Data in the format of an old style VTK file.
    filedata = Property(Str, depends_on='dataset')
    def _get_filedata(self):
        f = tempfile.NamedTemporaryFile(suffix='.vtk')
        print f.name
        from IPython.core.debugger import Tracer; Tracer()()
        writer = tvtk.PolyDataWriter(
            input=self.dataset,
            file_name=f.name
        )
        writer.write()
        return f.read()

    # The colors to use for the points, in json format.
    colors = Property(Str, depends_on='dataset')
    def _get_colors(self):
        scm = self.module_manager.scalar_lut_manager
        scalars = self.dataset.point_data.scalars

        colors = scm.lut.map_scalars(scalars, 0, -1).to_array()/255.0
        colors_on_points = colors[self._point_indices()]

        return json.dumps(colors_on_points.tolist())

    # The type of the mesh, for now only polygons are supported.
    type = Str("POLYGONS")

    #### Private protocol #####################################################

    def _point_indices(self):
        """
        Given the dataset, obtain the polygon connectivity array and generate
        the indices of the points in the polygon.
        """
        conn = self.dataset.polys.to_array()
        npoly = conn.size / 4
        choice = np.zeros(npoly*3, dtype=int)
        for start in (1, 2, 3):
            choice[start-1::3] = np.arange(start, npoly*4, step=4)
        return conn[choice]


#### Controller layer ####

class Plotter3D(HasTraits):

    #: expression to be visualized
    expression = Str
    def _expression_changed(self, expr):
        if self.plot is None:
            x, y, z = np.mgrid[-5:5:32j, -5:5:32j, -5:5:32j]
        else:
            x, y, z = self.x, self.y, self.z
        g = np.__dict__
        try:
            s = eval(expr, g, dict(x=x, y=y, z=z))
        except:
            pass
        else:
            if self.plot is None:
                self.x, self.y, self.z = x, y, z
                self.plot = mlab.contour3d(x, y, z, s, contours=self.n_contour)
            else:
                self.plot.mlab_source.set(scalars=s)
            self._update_mesh_data()

    #: number of contours for the visualization
    n_contour = Int(2)
    def _n_contour_changed(self, value):
        if 0 < value < 20:
            if self.plot:
                self.plot.contour.number_of_contours = value
                self._update_mesh_data()

    plot = Instance(PipelineBase)

    mesh_data = Instance(MeshData, ())
    def _mesh_data_default(self):
        return MeshData(
            dataset=self.plot.contour.outputs[0],
            module_manager=self.plot.module_manager
        )

    def _update_mesh_data(self):
        self.mesh_data.dataset = self.plot.contour.outputs[0]

#### UI layer ####

template = Template(html_file='mayavi_webgl_demo.html')

#### Entry point ####

def main():
    plotter = Plotter3D(expression="x*x*0.5 + y*y + z*z*2.0", n_contour=4)
    app = WebApp(template=template, context={'plotter': plotter}, port=8888)
    app.start()

if __name__ == '__main__':
    main()
