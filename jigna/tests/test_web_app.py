# Standard library
import socket
import threading
import unittest
import urllib2
from unittest import skip

# Enthought library
from traits.api import HasTraits, Str, Int

# Third party libraries
try:
    import tornado
    from tornado.testing import AsyncHTTPTestCase
    from selenium import webdriver
except ImportError:
    raise unittest.SkipTest("Tornado not installed")

# Local library
from jigna.api import WebApp
from jigna.api import Template
from jigna.utils.web import get_free_port

class MyModel(HasTraits):
    attr1 = Str
    attr2 = Int

@skip("Web tests don't work at the moment")
class TestWebApp(AsyncHTTPTestCase):

    def setUp(self):
        self.template = Template(body_html="Hello")
        self.model = MyModel(attr1="Attr1", attr2=2)
        self.port = get_free_port()
        self.app = WebApp(
            template=self.template,
            context={'model': self.model},
            port=self.port
        )
        print self.port

    def get_app(self):
        return self.app.create_application()

    def test_application_is_created(self):
        # Create an application
        application = self.get_app()

        # Check if a tornado application was created
        self.assertIsNotNone(application)
        self.assertIsInstance(application, tornado.web.Application)

    def test_application_is_running_on_given_port(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)

    def _test_browser_can_connect_to_application(self):
        # Create an application
        qwidget = self.app.create_widget()

        # Check if the widget has html loaded in it
        frame = qwidget.page().mainFrame()
        self.assertIsInstance(frame.toHtml(), basestring)
        self.assertGreater(len(frame.toHtml()), 0)

    def _test_browser_can_access_jigna(self):
        # Create a widget
        qwidget = self.app.create_widget()

        # Check if `jigna` was loaded on the JS side
        jigna = self.app.execute_js("jigna");
        self.assertIsNotNone(jigna)

    def _test_jigna_was_initialized(self):
        # Create a widget
        qwidget = self.app.create_widget()

        # Check if `jigna` was initialised on the JS side
        client = self.app.execute_js("jigna.client");
        self.assertIsNotNone(client)

    def _test_jigna_was_initialized_with_python_models(self):
        # Create a widget
        qwidget = self.app.create_widget()

        # Check if `jigna` was initialised with the correct python models
        # (check by making sure that primitive variables are the same)
        attr1 = self.app.execute_js("jigna.models.model.attr1")
        attr2 = self.app.execute_js("jigna.models.model.attr2")
        self.assertEqual(attr1, self.model.attr1)
        self.assertEqual(attr2, self.model.attr2)

if __name__ == "__main__":
    unittest.main()
