
import time
import unittest

from test_jigna_web import TestJignaWebSync, Person

class TestJignaWebAsync(TestJignaWebSync):
    @classmethod
    def setUpClass(cls):
        super(TestJignaWebAsync, cls).setUpClass(port=8889)
        cls.browser.execute_script('jigna.async = true;')

    def reset_user_var(self):
        self.execute_js("jigna.user = undefined;")

    def get_attribute(self, js, expect):
        self.reset_user_var()
        get_js = """jigna.get_attribute(\'%s\', function(result) {jigna.user = result;})"""%js
        self.execute_js(get_js)

        check_js = "return jigna.user;"
        result = self.execute_js(check_js)
        while result is None and expect is not None:
            time.sleep(0.1)
            result = self.execute_js(check_js)
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
        self.get_attribute("jigna.models.model.spouse", wilma)
        self.execute_js("var x; jigna.models.model.method(jigna.models.model.spouse).done(function(r){x=r;}); return x;")
        self.assertEqual(fred.called_with, wilma)



# Delete this so running just this file does not run all the tests.
del TestJignaWebSync

if __name__ == "__main__":
    unittest.main()
