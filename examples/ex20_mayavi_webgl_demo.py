""" This example shows how to show mayavi in the web version using the webGL
backend for VTK.
"""

#### Imports ####
from __future__ import print_function

import json
import numpy as np
from mayavi import mlab
from mayavi.core.api import PipelineBase
from traits.api import HasTraits, Instance, Int, Str
from tvtk.api import tvtk
from jigna.web_app import WebApp
from jigna.template import Template
from tornado.ioloop import IOLoop

mlab.options.offscreen = True
mlab.options.backend = 'test'

#### Domain Model ####

class MeshData(HasTraits):

    # Data in the format of an old style VTK file.
    filedata = Str

    # The colors to use for the points, in json format.
    colors = Str

    # The type of the mesh, for now only polygons are supported.
    type = Str("POLYGONS")

    @classmethod
    def from_dataset(cls, dataset, module_manager):
        filedata = cls._dataset_to_string(dataset)
        colors = cls._dataset_to_colors(dataset, module_manager)

        return MeshData(filedata=filedata, colors=colors)

    #### Private protocol #####################################################

    @classmethod
    def _dataset_to_string(cls, dataset):
        """
        Convert the dataset to a vtk filedata string.
        """
        writer = tvtk.PolyDataWriter(
            input=dataset,
            write_to_output_string=True
        )
        writer.write()
        return writer.output_string

    @classmethod
    def _dataset_to_colors(cls, dataset, module_manager):
        """
        Given the dataset, extract the colors array in a jsonized format.
        """
        scm = module_manager.scalar_lut_manager
        scalars = dataset.point_data.scalars

        colors = scm.lut.map_scalars(scalars, 0, -1).to_array()/255.0
        colors_on_points = colors[cls._point_indices(dataset)]

        return json.dumps(colors_on_points.tolist())

    @classmethod
    def _point_indices(cls, dataset):
        """
        Given the dataset, obtain the polygon connectivity array and generate
        the indices of the points in the polygon.
        """
        conn = dataset.polys.to_array()
        npoly = conn.size / 4
        choice = np.zeros(npoly*3, dtype=int)
        for start in (1, 2, 3):
            choice[start-1::3] = np.arange(start, npoly*4, step=4)
        return conn[choice]

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

    def _update_mesh_data(self):
        self.mesh_data.copy_traits(
            MeshData.from_dataset(
                dataset=self.plot.contour.outputs[0],
                module_manager=self.plot.module_manager
            )
        )

#### UI layer ####

template = Template(html_file='ex20_mayavi_webgl_demo.html')

#### Entry point ####

def main():
    # Start the tornado ioloop application
    ioloop = IOLoop.instance()

    # Instantiate the domain model
    plotter = Plotter3D(expression="x*x*0.5 + y*y + z*z*2.0", n_contour=4)

    # Create a web app serving the view with the domain model added to its
    # context.
    app = WebApp(template=template, context={'plotter': plotter})
    app.listen(8000)

    # Start serving the web app on port 8000.
    print('Serving on port 8000...')
    ioloop.start()

if __name__ == '__main__':
    main()
