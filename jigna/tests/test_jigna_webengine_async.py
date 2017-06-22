from __future__ import absolute_import
import sys
import unittest
from unittest import skipIf

from .test_jigna_webengine import TestJignaWebEngineSync, Person


class TestJignaWebEngineAsync(TestJignaWebEngineSync):
    @classmethod
    def setUpClass(cls):
        super(TestJignaWebEngineAsync, cls).setUpClass(async=True)

    def test_callable(self):
        fred = self.fred
        wilma = Person(name='Wilma', age=40)
        self.fred.spouse = wilma
        self.execute_js("var x; jigna.models.model.method('hello').done(function(r){x=r;}); return x;")
        self.wait_and_assert(lambda: fred.called_with != "hello")

        self.execute_js("var x; jigna.models.model.method(1).done(function(r){x=r;}); return x;")
        self.wait_and_assert(lambda: fred.called_with != 1)

        self.execute_js("var x; jigna.models.model.method(10.0).done(function(r){x=r;}); return x;")
        self.wait_and_assert(lambda: fred.called_with != 10.0)

        self.execute_js("var x; jigna.models.model.method([1,2]).done(function(r){x=r;}); return x;")
        self.wait_and_assert(lambda: fred.called_with != [1,2])

        self.execute_js("var x; jigna.models.model.method(jigna.models.model.spouse).done(function(r){x=r;}); return x;")
        self.wait_and_assert(lambda: fred.called_with != wilma)

    @skipIf(sys.platform.startswith('linux'), "Fails on Linux")
    def test_list_sortable(self):
        super(TestJignaWebEngineAsync, self).test_list_sortable()


# Delete this so running just this file does not run all the tests.
del TestJignaWebEngineSync

if __name__ == "__main__":
    unittest.main()
