from jigna.api import HTMLWidget, Template
from jigna.qt import QtWebKit, QtGui

from traits.api import HasTraits, Str, Int

import unittest

class MyModel(HasTraits):
    attr1 = Str
    attr2 = Int

class TestHTMLWidget(unittest.TestCase):

    def setUp(self):
        self.model = MyModel(attr1="Attr1", attr2=2)
        self.template = Template(body_html="")

        self.app = QtGui.QApplication.instance() or QtGui.QApplication([])

    def test_widget_is_created(self):
        # Create a widget
        widget = HTMLWidget(
            template=self.template, context={'model': self.model}
        )

        # Check if a qwebview widget was created
        self.assertIsNotNone(widget)
        self.assertIsInstance(widget, QtGui.QWidget)
        self.assertIsInstance(widget.children()[0], QtWebKit.QWebView)

    def test_created_widget_loads_html(self):
        # Create a widget
        widget = HTMLWidget(
            template=self.template, context={'model': self.model}
        )

        # Check if the widget has html loaded in it
        webview = widget.children()[0]
        frame = webview.page().mainFrame()
        self.assertIsInstance(frame.toHtml(), basestring)
        self.assertGreater(len(frame.toHtml()), 0)

    def test_created_widget_can_access_jigna(self):
        # Create a widget
        widget = HTMLWidget(
            template=self.template, context={'model': self.model}
        )

        # Check if `jigna` was loaded on the JS side
        jigna = widget.execute_js("jigna");
        self.assertIsNotNone(jigna)

    def test_jigna_was_initialized(self):
        # Create a widget
        widget = HTMLWidget(
            template=self.template, context={'model': self.model}
        )

        # Check if `jigna` was initialised on the JS side
        client = widget.execute_js("jigna.client");
        self.assertIsNotNone(client)

    def test_jigna_was_initialized_with_python_models(self):
        # Create a widget
        widget = HTMLWidget(
            template=self.template, context={'model': self.model}
        )

        # Check if `jigna` was initialised with the correct python models
        # (check by making sure that primitive variables are the same)
        attr1 = widget.execute_js("jigna.models.model.attr1")
        attr2 = widget.execute_js("jigna.models.model.attr2")
        self.assertEqual(attr1, self.model.attr1)
        self.assertEqual(attr2, self.model.attr2)

    def test_two_widgets_are_created(self):
        HTMLWidget(template=self.template, context={'model': self.model})
        HTMLWidget(template=self.template, context={'model': self.model})

        # If you arrive here, it means the test passed
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
