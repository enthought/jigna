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
        get_js = """jigna.wait_for(\'%s\').done(function(result)
                                {jigna.user = result;})"""%js
        self.execute_js(get_js)

        check_js = "return jigna.user;"
        result = self.execute_js(check_js)
        count = 0
        while (result != expect) and count < 10:
            self.execute_js(get_js)
            time.sleep(0.025)
            result = self.execute_js(check_js)
            count += 1
        self.reset_user_var()
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
