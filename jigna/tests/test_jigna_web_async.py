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

    def test_list_sortable(self):
        # Given
        fred = self.fred
        self.execute_js(
            "jigna.models.model.fruits = ['peach', 'apple', 'banana']"
        )
        self.assertJSEqual(
            "jigna.models.model.fruits", ['peach', 'apple', 'banana']
        )

        # When
        self.execute_js("jigna.models.model.fruits.sort()")
        self.get_attribute("jigna.models.model.fruits", None)

        # Then
        self.assertJSEqual(
            "jigna.models.model.fruits", ['apple', 'banana', 'peach']
        )
        self.assertEqual(fred.fruits, ['apple', 'banana', 'peach'])



# Delete this so running just this file does not run all the tests.
del TestJignaWebSync

if __name__ == "__main__":
    unittest.main()
