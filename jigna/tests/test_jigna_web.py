from jigna.api import View
from threading import Thread

from selenium import webdriver
import unittest

# Local imports.
from test_jigna_qt import TestJignaQt, Person, body_html


class TestJignaWeb(TestJignaQt):
    @classmethod
    def setUpClass(cls):
        person_view = View(body_html=body_html)
        fred = Person(name='Fred', age=42)
        t = Thread(target=person_view.serve, kwargs=dict(model=fred))
        t.setDaemon(True)
        t.start()

        browser = webdriver.Firefox()
        browser.get('http://localhost:8888')
        cls.person_view = person_view
        cls.fred = fred
        cls.browser = browser

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()

    def setUp(self):
        cls = self.__class__
        self.person_view = cls.person_view
        self.browser = cls.browser
        self.fred = cls.fred
        self.fred.spouse = None
        self.fred.fruits = []
        self.fred.friends = []

    def execute_js(self, js):
        result = self.browser.execute_script(js)
        return result

    def assertJSEqual(self, js, value):
        result = self.execute_js('return ' + js + ';')
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
