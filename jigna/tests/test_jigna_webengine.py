from __future__ import absolute_import
from textwrap import dedent
from threading import Thread
import time
import sys
import unittest

try:
    from tornado.ioloop import IOLoop
except ImportError:
    raise unittest.SkipTest("Tornado not installed")

# Local imports.
from jigna.utils.web import get_free_port
from .test_jigna_qt import TestJignaQt, Person, body_html, AddressBook


def patch_sys_modules():
    backup = sys.modules.copy()
    for name in list(sys.modules.keys()):
        if 'PySide' in name or 'PyQt' in name:
            del sys.modules[name]

    return backup


def restore_sys_modules(backup):
    sys.modules = backup


def assert_no_qt_in_sys_modules():
    for name in list(sys.modules.keys()):
        if 'PySide' in name or 'PyQt' in name:
            raise AssertionError("Qt import found: %s." % name)


def start_io_loop():
    ioloop = IOLoop.instance()
    ioloop.make_current()
    ioloop.start()


def stop_io_loop():
    IOLoop.instance().stop()


class TestJignaWebEngineSync(TestJignaQt):
    @classmethod
    def setUpClass(cls, async=False):
        from jigna.template import Template
        from jigna.web_app import WebApp
        from jigna.utils import gui
        from jigna.qt import QtWebEngine, QtCore
        if QtWebEngine is None:
            raise unittest.SkipTest('Needs QtWebEngine')
        gui.qapp()
        fred = Person(name='Fred', age=42)
        addressbook = AddressBook()
        template = Template(body_html=body_html, async=async)
        port = get_free_port()
        app = WebApp(
            template=template,
            context={'model':fred, 'addressbook': addressbook}, async=async
        )
        app.listen(port)

        # Start the tornado server in a different thread so that we can write
        # test statements here in the main loop.
        t = Thread(target=start_io_loop)
        t.setDaemon(True)
        t.start()

        browser = QtWebEngine.QWebEngineView()
        browser.load(QtCore.QUrl('http://localhost:%d' % port))
        gui.process_events()
        cls.app = app
        cls.fred = fred
        cls.browser = browser
        cls.addressbook = addressbook
        cls.thread = t

    @classmethod
    def tearDownClass(cls):
        cls.browser.destroy()

        IOLoop.instance().add_callback(stop_io_loop)
        thread = cls.thread
        count = 0
        while thread.is_alive() and count < 50:
            time.sleep(0.1)
        cls.thread.join()

    def setUp(self):
        cls = self.__class__
        self.app = cls.app
        self.browser = cls.browser
        self.fred = cls.fred
        self.fred.spouse = None
        self.fred.fruits = []
        self.fred.friends = []
        # Wait for the model to be setup before running the tests.
        self.get_attribute('jigna.models.model.name', self.fred.name)

    def execute_js(self, js):
        # wrap the code in an expression function evaluation
        js_code = '(function(){%s})()' % js
        js_result = []
        def callback(result):
            js_result.append(result)
        self.browser.page().runJavaScript(js_code, callback)
        while not js_result:
            self.process_events()
        return js_result[0]

    def get_attribute(self, js, expect):
        get_js = dedent("""
        var result;
        try {
            result = eval(%r);
        } catch (err) {
            result = undefined;
        }
        return result;
        """%js)
        self.execute_js(get_js)

        check_js = get_js
        result = self.execute_js(check_js)
        count = 0
        while result != expect and count < 20:
            time.sleep(0.1)
            result = self.execute_js(check_js)
            count += 1
        return result

    def assertJSEqual(self, js, value):
        result = self.get_attribute(js, value)
        if isinstance(value, (list, tuple)):
            msg = "Lengths different: expected %d, got %d" % \
                (len(value), len(result))
            self.assertEqual(len(value), len(result), msg)
            for index in range(len(value)):
                expect = value[index]
                got = result[str(index)]
                if got != expect:
                    got = self.get_attribute(js+"['%d']"%index, expect)
                msg = "%s[%s] != %s, got %s"%(js, index, expect, got)
                self.assertEqual(expect, got, msg)
        else:
            msg = "%s != %s, got %s"%(js, value, result)
            self.assertEqual(value, result, msg)

    def test_reload_works_correctly(self):
        # Given
        fred = self.fred
        fred.fruits = ["peach", "pear"]
        dino = Person(name="Dino", age=10)
        fred.friends = [dino]
        fred.phonebook = {'joe' : 123, 'joan' : 345}
        wilma = Person(name='Wilma', age=40)
        fred.spouse = wilma

        # When
        self.execute_js("window.location.reload();")
        time.sleep(1)
        self.get_attribute("jigna.models.model.name", fred.name)

        # Then
        self.assertJSEqual("jigna.models.model.name", fred.name)
        self.assertJSEqual("jigna.models.model.friends[0].name", "Dino")
        self.assertJSEqual("jigna.models.model.friends[0].age", 10)
        self.assertJSEqual("jigna.models.model.phonebook.joe", 123)
        self.assertJSEqual("jigna.models.model.phonebook.joan", 345)
        self.assertJSEqual("jigna.models.model.phonebook", fred.phonebook)
        self.assertJSEqual("jigna.models.model.fruits", fred.fruits)
        self.assertJSEqual("jigna.models.model.spouse.name", 'Wilma')
        self.assertJSEqual("jigna.models.model.spouse.age", 40)

# Delete this so running just this file does not run all the tests.
del TestJignaQt

if __name__ == "__main__":
    unittest.main()

#### EOF ######################################################################
