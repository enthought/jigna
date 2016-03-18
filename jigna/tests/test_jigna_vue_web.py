from threading import Thread
import unittest

try:
    from tornado.ioloop import IOLoop
    from selenium import webdriver
except ImportError:
    raise unittest.SkipTest("Tornado not installed")

# Local imports.
from jigna.api import VueTemplate, WebApp
from jigna.utils.web import get_free_port
from test_jigna_web import TestJignaWebSync, Person
from test_jigna_vue_qt import body_vue_html

class TestJignaVueWebSync(TestJignaWebSync):
    @classmethod
    def setUpClass(cls, async=False):
        ioloop = IOLoop.instance()
        fred = Person(name='Fred', age=42)
        template = VueTemplate(body_html=body_vue_html, async=async)
        port = get_free_port()
        app = WebApp(template=template, context={'model':fred})
        app.listen(port)

        # Start the tornado server in a different thread so that we can write
        # test statements here in the main loop
        t = Thread(target=ioloop.start)
        t.setDaemon(True)
        t.start()

        browser = webdriver.Firefox()
        browser.get('http://localhost:%d'%port)
        cls.app = app
        cls.fred = fred
        cls.browser = browser


del TestJignaWebSync


if __name__ == "__main__":
    unittest.main()
