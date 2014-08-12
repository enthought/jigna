from jigna.api import QtApp
from jigna.api import Template

from pyface.qt import QtWebKit, QtGui
from pyface.gui import GUI

import unittest

class TestQtApp(unittest.TestCase):

    def test_widget_is_created(self):
        # Create a QtApp with an empty template and empty context
        template = Template(body_html="")
        app = QtApp(template=template, context={})

        # Create a widget
        qwidget = app.create_widget()

        # Check if a qwebview widget was created
        self.assertIsNotNone(qwidget)
        self.assertIsInstance(qwidget, QtGui.QWidget)
        self.assertIsInstance(qwidget, QtWebKit.QWebView)

    def test_created_widget_loads_html(self):
        # Create a QtApp with an empty template and empty context
        template = Template(body_html="")
        app = QtApp(template=template, context={})

        # Create a widget
        qwidget = app.create_widget()
        GUI.process_events()

        # Check if the widget has html loaded in it
        frame = qwidget.page().mainFrame()
        self.assertIsInstance(frame.toHtml(), basestring)
        self.assertGreater(len(frame.toHtml()), 0)

if __name__ == "__main__":
    unittest.main()
