from jigna.api import QtApp
from jigna.api import Template

from pyface.qt import QtWebKit, QtGui
from pyface.gui import GUI

from traits.api import HasTraits, Str, Int

import unittest

class MyModel(HasTraits):
    attr1 = Str
    attr2 = Int

class TestQtApp(unittest.TestCase):

    def setUp(self):
        self.template = Template(body_html="")
        self.model = MyModel(attr1="Attr1", attr2=2)
        self.app = QtApp(template=self.template, context={'model': self.model})

    def test_widget_is_created(self):
        # Create a widget
        qwidget = self.app.create_widget()

        # Check if a qwebview widget was created
        self.assertIsNotNone(qwidget)
        self.assertIsInstance(qwidget, QtGui.QWidget)
        self.assertIsInstance(qwidget, QtWebKit.QWebView)

    def test_created_widget_loads_html(self):
        # Create a widget
        qwidget = self.app.create_widget()
        GUI.process_events()

        # Check if the widget has html loaded in it
        frame = qwidget.page().mainFrame()
        self.assertIsInstance(frame.toHtml(), basestring)
        self.assertGreater(len(frame.toHtml()), 0)

    def test_created_widget_can_access_jigna(self):
        # Create a widget
        qwidget = self.app.create_widget()
        GUI.process_events()

        # Check if `jigna` was loaded on the JS side
        jigna = self.app.execute_js("jigna");
        self.assertIsNotNone(jigna)

    def test_jigna_was_initialized(self):
        # Create a widget
        qwidget = self.app.create_widget()
        GUI.process_events()

        # Check if `jigna` was initialised on the JS side
        client = self.app.execute_js("jigna.client");
        self.assertIsNotNone(client)

    def test_jigna_was_initialized_with_python_models(self):
        # Create a widget
        qwidget = self.app.create_widget()
        GUI.process_events()

        # Check if `jigna` was initialised with the correct python models
        # (check by making sure that primitive variables are the same)
        attr1 = self.app.execute_js("jigna.models.model.attr1")
        attr2 = self.app.execute_js("jigna.models.model.attr2")
        self.assertEqual(attr1, self.model.attr1)
        self.assertEqual(attr2, self.model.attr2)

if __name__ == "__main__":
    unittest.main()
