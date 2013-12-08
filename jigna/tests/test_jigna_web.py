from jigna.api import View
from traits.api import Dict, HasTraits, Instance, Int, Str, List
from threading import Thread

from selenium import webdriver
import unittest

# Local imports.
from test_jigna_qt import TestJignaQt, Person

#### Test model ####

#class Person(HasTraits):
#    name = Str
#    age  = Int
#    spouse = Instance('Person')
#    fruits = List(Str)
#    friends = List(Instance('Person'))
#    phonebook = Dict(Str, Int)
#
#    def method(self, value):
#        self.called_with = value

#### UI for model ####

body_html = """
    <div>
      Name: <input ng-model="model.name">
      Age: <input ng-model="model.age" type='number'>
      <br/>
      Fruits:
      <ul>
        <li ng-repeat="fruit in model.fruits track by $index">
          <input ng-model="model.fruits[$index]">
        </li>
      </ul>

      <br/>

      Friends:
      <ul>
        <li ng-repeat="friend in model.friends">
          Name: <input ng-model="friend.name">
          Age: <input ng-model="friend.age" type="number">
          Fruits:
          <ul>
            <li ng-repeat="fruit in friend.fruits track by $index">
              <input ng-model="friend.fruits[$index]">
            </li>
          </ul>
        </li>
      </ul>
    </div>
"""

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


del TestJignaQt

if __name__ == "__main__":
    unittest.main()

#### EOF ######################################################################
