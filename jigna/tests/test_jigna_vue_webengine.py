from __future__ import absolute_import
import sys
from threading import Thread
import unittest

try:
    from tornado.ioloop import IOLoop
except ImportError:
    raise unittest.SkipTest("Tornado not installed")

# Local imports.
from jigna.utils.web import get_free_port
from .test_jigna_webengine import TestJignaWebEngineSync, Person, AddressBook, \
    patch_sys_modules, start_io_loop
from .test_jigna_vue_qt import body_vue_html


class TestJignaVueWebEngineSync(TestJignaWebEngineSync):
    @classmethod
    def setUpClass(cls, async=False):
        from jigna.vue_template import VueTemplate
        from jigna.web_app import WebApp
        from jigna.utils import gui
        from jigna.qt import QtWebEngine, QtCore
        if QtWebEngine is None:
            raise unittest.SkipTest('Needs QtWebEngine')
        gui.qapp()
        fred = Person(name='Fred', age=42)
        addressbook = AddressBook()
        template = VueTemplate(body_html=body_vue_html, async=async)
        port = get_free_port()
        app = WebApp(
            template=template,
            context={'model':fred, 'addressbook':addressbook},
            async=async
        )
        app.listen(port)

        # Start the tornado server in a different thread so that we can write
        # test statements here in the main loop
        t = Thread(target=start_io_loop)
        t.setDaemon(True)
        t.start()

        browser = QtWebEngine.QWebEngineView()
        browser.load(QtCore.QUrl('http://localhost:%d' % port))
        browser.show()
        gui.process_events()
        cls.app = app
        cls.fred = fred
        cls.browser = browser
        cls.addressbook = addressbook
        cls.thread = t


del TestJignaWebEngineSync


if __name__ == "__main__":
    unittest.main()
