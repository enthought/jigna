from jigna.api import View
from threading import Thread
import unittest

from selenium import webdriver

# Local imports.
from test_jigna_qt import TestJignaQt, Person, body_html


class TestJignaWebSync(TestJignaQt):
    @classmethod
    def setUpClass(cls, port=8888):
        person_view = View(body_html=body_html)
        fred = Person(name='Fred', age=42)
        t = Thread(target=person_view.serve, kwargs=dict(port=port, model=fred))
        t.setDaemon(True)
        t.start()

        browser = webdriver.Firefox()
        browser.get('http://localhost:%d'%port)
        cls.person_view = person_view
        cls.fred = fred
        cls.browser = browser

    @classmethod
    def tearDownClass(cls):
        from tornado.ioloop import IOLoop
        cls.browser.quit()
        IOLoop.instance().stop()
        import time
        time.sleep(1)

    def setUp(self):
        cls = self.__class__
        self.person_view = cls.person_view
        self.browser = cls.browser
        self.fred = cls.fred
        self.fred.spouse = None
        self.fred.fruits = []
        self.fred.friends = []

    def execute_js(self, js):
        return self.browser.execute_script(js)

    def get_attribute(self, js, expect):
        return self.execute_js("return " + js + ";")

    def assertJSEqual(self, js, value):
        result = self.get_attribute(js, value)
        if isinstance(value, (list, tuple)):
            msg = "Lengths different: expected %d, got %d" % \
                (len(value), len(result))
            self.assertEqual(len(value), len(result), msg)
            for index in range(len(value)):
                expect = value[index]
                got = result[index]
                msg = "%s[%s] != %s, got %s"%(js, index, expect, got)
                self.assertEqual(expect, got, msg)
        else:
            msg = "%s != %s, got %s"%(js, value, result)
            self.assertEqual(value, result, msg)

    def test_instance_trait(self):
        # Overridden to work with the web backend.
        self.assertJSEqual("jigna.models.model.spouse", None)
        wilma = Person(name='Wilma', age=40)
        self.fred.spouse = wilma
        self.get_attribute("jigna.models.model.spouse.name", "")
        self.assertJSEqual("jigna.models.model.spouse.name", 'Wilma')
        self.assertJSEqual("jigna.models.model.spouse.age", 40)

        # Set in the JS side.
        self.execute_js("jigna.models.model.spouse.name = 'Wilmaji'")
        self.execute_js("jigna.models.model.spouse.age = 41")
        self.assertEqual(wilma.name, "Wilmaji")
        self.assertEqual(wilma.age, 41)


# Delete this so running just this file does not run all the tests.
del TestJignaQt

if __name__ == "__main__":
    unittest.main()

#### EOF ######################################################################
