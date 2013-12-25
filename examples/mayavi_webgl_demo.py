
import numpy as np
from mayavi import mlab
from mayavi.core.api import PipelineBase
from tvtk.api import tvtk
from traits.api import HasTraits, Instance, Int, Str

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


def get_data1():
    s = mlab.test_contour3d()
    return s.contour.outputs[0]


def get_data():
    #s = mlab.test_contour3d()
    #return s.contour.outputs[0]
    s = mlab.test_plot3d()
    return s.module_manager.source.outputs[0]


class Model3D(HasTraits):
    expression = Str("x*x*0.5 + y*y + z*z*2.0")
    plot_output = Str
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
            self.plot_output = dataset_to_string(self.plot.contour.outputs[0])

    def _n_contour_changed(self, value):
        self.plot.contour.number_of_contours = value
        self.plot_output = dataset_to_string(self.plot.contour.outputs[0])



body_html = """
<script type="text/javascript" src="http://get.goXTK.com/xtk.js"></script>
<script>
window.on_data_changed = function(new_data) {
    var arr = window.strtobuf(new_data);
    var mesh = window.mesh;
    mesh.file = null;
    mesh.filedata = arr;
    mesh._filedata = arr;
    var p = new X.parserVTK();
    p.parse(mesh, mesh, arr, null);
    mesh.modified();
};

window.strtobuf = function (str) {
    var buf = new Uint8Array(str.length);
    for (var i=0; i<str.length; i++) {
        buf[i] = str.charCodeAt(i);
    }
    return buf;
};


window.onload = function() {
var r = new X.renderer3D();
window.renderer = r;
r.container = "3d-scene";
r.init();

var mesh = new X.mesh();
window.mesh = mesh;
//mesh.file = 'foo.vtk';
//mesh.filedata = jigna.models.model.plot_data;

// add the object
r.add(mesh);

// .. and render it
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
