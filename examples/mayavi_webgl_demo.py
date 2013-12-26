import json
import numpy as np
from mayavi import mlab
from mayavi.core.api import PipelineBase
from traits.api import HasTraits, Instance, Int, Str
from tvtk.api import tvtk

mlab.options.offscreen = True
mlab.options.backend = 'test'

def dataset_to_string(dataset, **kwargs):
    """Given a TVTK `dataset` this writes the `dataset` to an old style VTK
    file.

    Any additional keyword arguments are passed to the writer used.
    """

    err_msg = "Can only write tvtk.DataSet instances "\
              "'got %s instead"%(dataset.__class__.__name__)
    assert isinstance(dataset, tvtk.DataSet), err_msg

    # Mapping to determine appropriate extension and writer.
    d2r = {'vtkImageData': ('.vti', tvtk.StructuredPointsWriter),
           'vtkRectilinearGrid': ('.vtr', tvtk.RectilinearGridWriter),
           'vtkStructuredGrid': ('.vts', tvtk.StructuredGridWriter),
           'vtkPolyData': ('.vtp', tvtk.PolyDataWriter),
           'vtkUnstructuredGrid': ('.vtu', tvtk.UnstructuredGridWriter)
           }

    for type in d2r:
        if dataset.is_a(type):
            datatype = d2r[type]
            break

    writer = datatype[1](write_to_output_string=True, input=dataset, **kwargs)
    writer.write()
    return writer.output_string

def get_point_idx_from_poly(dataset):
    """Given the dataset, this gets the polygon connectivity array
    and generates the indices of the points in the polygon.
    """
    conn = dataset.polys.to_array()
    npoly = conn.size/4
    choice = np.zeros(npoly*3, dtype=int)
    for start in (1, 2, 3):
        choice[start-1::3] = np.arange(start, npoly*4, step=4)
    return conn[choice]

def get_colors(dataset, module_manager):
    scm = module_manager.scalar_lut_manager
    scalars = dataset.point_data.scalars
    return scm.lut.map_scalars(scalars, 0, -1).to_array()/255.


class MeshData(HasTraits):
    # Optional data from a file that can be used.
    filedata = Str('')
    # The points for the mesh, this is a json string of a list.
    points = Str
    # The normals for the mesh, this is a json string of a list.
    normals = Str
    # The colors to use for the points, again a json string.
    colors = Str

    # The type of the mesh, for now only polygons are supported.
    type = Str("POLYGONS")

    @classmethod
    def from_file(cls, dataset, module_manager):
        filedata = dataset_to_string(dataset)
        point_idx = get_point_idx_from_poly(dataset)
        colors = get_colors(dataset, module_manager)
        colors_xtk = colors[point_idx]
        result = MeshData(filedata=filedata,
                          colors=json.dumps(colors_xtk.tolist()))
        return result

    @classmethod
    def from_data(cls, dataset, module_manager):
        points = dataset.points.to_array()
        normals = dataset.point_data.normals.to_array()
        colors = get_colors(dataset, module_manager)
        point_idx = get_point_idx_from_poly(dataset)
        result = MeshData()
        data = {'points': points, 'normals': normals, 'colors': colors}
        for attr, array in data.iteritems():
            arr_xtk = array[point_idx]
            setattr(result, attr, json.dumps(arr_xtk.tolist()))
        return result


class Model3D(HasTraits):
    expression = Str("x*x*0.5 + y*y + z*z*2.0")
    plot_output = Instance(MeshData)
    n_contour = Int(4)

    plot = Instance(PipelineBase)

    def __init__(self, **traits):
        super(Model3D, self).__init__(**traits)
        self._expression_changed(self.expression)

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
            self._setup_plot_output()

    def _n_contour_changed(self, value):
        if 0 < value < 20:
            self.plot.contour.number_of_contours = value
            self._setup_plot_output()

    def _setup_plot_output(self):
        self.plot_output = MeshData.from_file(self.plot.contour.outputs[0],
                                              self.plot.module_manager)


body_html = """
<script type="text/javascript" src="http://get.goXTK.com/xtk.js"></script>
<script>
window.on_data_changed = function(new_data) {
    var mesh = window.mesh;
    mesh.file = null;
    if (new_data.filedata.length > 0) {
        var arr = window.strtobuf(new_data.filedata);
        mesh.filedata = arr;
        var p = new X.parserVTK();
        p.parse(mesh, mesh, arr, null);
    }
    else {
        mesh.points = window.array_to_triplets(new_data.points);
        if (new_data.normals.length > 0) {
            mesh.normals = window.array_to_triplets(new_data.normals);
        }
        mesh.type = new_data.type;
    }
    if (new_data.colors.length > 0) {
        mesh.colors = window.array_to_triplets(new_data.colors);
    }
    mesh.modified();
};

window.strtobuf = function (str) {
    var buf = new Uint8Array(str.length);
    for (var i=0; i<str.length; i++) {
        buf[i] = str.charCodeAt(i);
    }
    return buf;
};

window.array_to_triplets = function(json_data) {
    var data = JSON.parse(json_data);
    var triplets = new X.triplets(4*3*data.length);
    for (var i=0; i<data.length; i++) {
        triplets.add(data[i][0], data[i][1], data[i][2]);
    }
    return triplets;
};

window.onload = function() {
    var r = new X.renderer3D();
    window.renderer = r;
    r.container = "3d-scene";
    r.init();

    var mesh = new X.mesh();
    window.mesh = mesh;

    r.add(mesh);
    r.render();

    window.on_data_changed(jigna.models.model.plot_output);

    $(document.body).scope().$watchCollection(
        "[model.expression, model.n_contour]",
        function (new_data) {
            console.log("Updating plot.");
            window.on_data_changed(jigna.models.model.plot_output);
        });

};

</script>
<div>
Expression: <input ng-model="model.expression">
<br>
Number of contours: <input type="number" ng-model="model.n_contour" min="1" max="10">

<div id="3d-scene" style="background-color: #000; height:80%;">
</div>
</div>
"""

def main():
    import webbrowser
    from jigna.api import View
    model = Model3D()
    view = View(body_html=body_html)
    webbrowser.open_new('http://localhost:8888')
    view.serve(model=model)

if __name__ == '__main__':
    main()
