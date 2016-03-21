import unittest
from unittest import skip
import time

from test_jigna_web import TestJignaWebSync, Person

class TestJignaWebAsync(TestJignaWebSync):
    @classmethod
    def setUpClass(cls):
        super(TestJignaWebAsync, cls).setUpClass(async=True)

    def get_attribute(self, js, expect):
        self.reset_user_var()
        get_js = """return %s;"""%js
        self.execute_js(get_js)

        check_js = get_js
        result = self.execute_js(check_js)
        count = 0
        while (result != expect) and count < 10:
            time.sleep(0.1)
            result = self.execute_js(check_js)
            count += 1
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
