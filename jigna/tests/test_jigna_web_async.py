import unittest
from unittest import skip
import time

from test_jigna_web import TestJignaWebSync, Person

class TestJignaWebAsync(TestJignaWebSync):
    @classmethod
    def setUpClass(cls):
        super(TestJignaWebAsync, cls).setUpClass(async=True)

    def _sleep(self):
        # Yield to the server thread.
        time.sleep(0)

    def setUp(self):
        super(TestJignaWebAsync, self).setUp()
        self.fred.on_trait_change(self._sleep)

    def tearDown(self):
        super(TestJignaWebAsync, self).tearDown()
        self.fred.on_trait_change(self._sleep, remove=True)

    def execute_js(self, js):
        self._sleep()
        result = super(TestJignaWebAsync, self).execute_js(js)
        self._sleep()
        return result

    def test_callable(self):
        fred = self.fred
        wilma = Person(name='Wilma', age=40)
        self.fred.spouse = wilma
        self.execute_js("var x; jigna.models.model.method('hello').done(function(r){x=r;}); return x;")
        self.assertEqual(fred.called_with, "hello")
        self.execute_js("var x; jigna.models.model.method(1).done(function(r){x=r;}); return x;")
        self.assertEqual(fred.called_with, 1)
        self.execute_js("var x; jigna.models.model.method(10.0).done(function(r){x=r;}); return x;")
        self.assertEqual(fred.called_with, 10.0)
        self.execute_js("var x; jigna.models.model.method([1,2]).done(function(r){x=r;}); return x;")
        self.assertEqual(fred.called_with, [1,2])
        self.execute_js("var x; jigna.models.model.method(jigna.models.model.spouse).done(function(r){x=r;}); return x;")
        self.assertEqual(fred.called_with, wilma)


# Delete this so running just this file does not run all the tests.
del TestJignaWebSync

if __name__ == "__main__":
    unittest.main()
