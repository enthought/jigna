import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from StringIO import StringIO
from traits.api import HasTraits, CInt, Str

def get_svg_plot():
    """Return SVG string of a matplotlib plot.
    """
    stream = StringIO()
    plt.savefig(stream, format='svg')
    stream.seek(0)
    return stream.buf

def get_png_plot():
    """Return PNG string of a matplotlib plot after base64 encoding it.
    """
    stream = StringIO()
    plt.savefig(stream, format='png')
    stream.seek(0)
    return stream.buf.encode('base64')


class Model(HasTraits):
    scaling_factor = CInt(1)

    plot_output = Str

    def _make_plot(self):
        x = np.linspace(-2*np.pi, 2*np.pi, 200)
        y = np.sin(self.scaling_factor*x)/x
        plt.clf()
        plt.plot(x, y)
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title("sin(%s x)/x"%self.scaling_factor)

    def _scaling_factor_changed(self, value):
        self._make_plot()
        self.plot_output = self.get_plot()

    def _plot_output_default(self):
        self._make_plot()
        return self.get_plot()

    def get_plot(self):
        return get_png_plot()

    def get_html(self):
        return self._get_png_html()

    def _get_svg_html(self):
        body_html = """
            <div>
            Scaling factor: <input type="range" ng-model="model.scaling_factor"
                            min=0 max=30><br>
            Plot:<br>
            <div ng-bind-html-unsafe="model.plot_output">{{model.plot_output}}</div>
            </div>
        """
        return body_html

    def _get_png_html(self):
        body_html = """
                <div>
                Scaling factor: <input type="range" ng-model="model.scaling_factor"
                                min=0 max=30><br>
                Plot:<br>
                <div>
                <img src="data:image/png;base64,{{model.plot_output}}">
                </div>
                </div>
            """
        return body_html


def test_standalone():
    model = Model()
    from jigna.api import View
    v = View(body_html=model.get_html())
    v.serve(model=model)


if __name__ == '__main__':
    test_standalone()
