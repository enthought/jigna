from traits.api import HasTraits, Instance, Int, Str, List
from jigna.api import JignaView
from pyface.gui import GUI

import unittest

#### Test model ####

class Person(HasTraits):
    name = Str
    age  = Int
    spouse = Instance('Person')
    fruits = List(Str)
    friends = List(Instance('Person'))

    def method(self, value):
        self.called_with = value

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

class TestJignaQt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        person_view = JignaView(body_html=body_html)
        fred = Person(name='Fred', age=42)
        person_view.show(model=fred)
        GUI.process_events()
        cls.person_view = person_view
        cls.fred = fred

    def setUp(self):
        cls = self.__class__
        self.person_view = cls.person_view
        self.bridge = self.person_view._broker.bridge
        self.fred = cls.fred
        self.fred.spouse = None
        self.fred.fruits = []
        self.fred.friends = []

    def execute_js(self, js):
        js = 'jigna.broker._scope.' + js
        GUI.process_events()
        result = self.bridge.execute_js(js)
        GUI.process_events()
        return result

    def assertJSEqual(self, js, value):
        result = self.execute_js(js)
        if isinstance(value, (list, tuple)):
            msg = "Lengths different: expected %d, got %d" % \
                (len(value), len(result))
            self.assertEqual(len(value), len(result), msg)
            for index in range(len(value)):
                expect = value[index]
                got = result[str(index)]
                msg = "%s[%s] != %s, got %s"%(js, index, expect, got)
                self.assertEqual(expect, got, msg)
        else:
            msg = "%s != %s, got %s"%(js, value, result)
            self.assertEqual(value, result, msg)

    def test_simple_primitive_traits(self):
        fred = self.fred
        fred.name = "Freddie"
        self.assertJSEqual("model.name", fred.name)
        fred.age = 43
        self.assertJSEqual("model.age", fred.age)

    def test_list_of_primitives(self):
        self.assertJSEqual("model.fruits", [])
        fred = self.fred
        fred.fruits = ["banana", "mango"]
        self.assertJSEqual("model.fruits", fred.fruits)

        # Now set the value in the JS side.
        self.execute_js("model.fruits[0] = 'peach'")
        self.assertEqual(fred.fruits, ["peach", "mango"])

        self.execute_js("model.fruits = ['apple']")
        self.assertEqual(fred.fruits, ["apple"])

    def test_instance_trait(self):
        self.assertJSEqual("model.spouse", '')
        wilma = Person(name='Wilma', age=40)
        self.fred.spouse = wilma
        self.assertJSEqual("model.spouse.name", 'Wilma')
        self.assertJSEqual("model.spouse.age", 40)

        # Set in the JS side.
        self.execute_js("model.spouse.name = 'Wilmaji'")
        self.execute_js("model.spouse.age = 41")
        self.assertEqual(wilma.name, "Wilmaji")
        self.assertEqual(wilma.age, 41)

    def test_list_instance(self):
        self.assertJSEqual("model.friends", [])
        barney = Person(name="Barney", age=40)
        fred = self.fred
        fred.friends = [barney]
        self.assertJSEqual("model.friends[0].name", "Barney")
        self.assertJSEqual("model.friends[0].age", 40)

        dino = Person(name="Dino", age=10)
        fred.friends.append(dino)
        self.assertJSEqual("model.friends[1].name", "Dino")
        self.assertJSEqual("model.friends[1].age", 10)
        self.execute_js("model.friends[0].name = 'Barneyji'")
        self.assertEqual(barney.name, "Barneyji")

    def test_callable(self):
        fred = self.fred
        wilma = Person(name='Wilma', age=40)
        self.fred.spouse = wilma
        self.execute_js("model.method('hello')")
        self.assertEqual(fred.called_with, "hello")
        self.execute_js("model.method(1)")
        self.assertEqual(fred.called_with, 1)
        self.execute_js("model.method(10.0)")
        self.assertEqual(fred.called_with, 10.0)
        self.execute_js("model.method([1, 2])")
        self.assertEqual(fred.called_with, [1,2])
        self.execute_js("model.method(jigna.broker._scope.model.spouse)")
        self.assertEqual(fred.called_with, wilma)

if __name__ == "__main__":
    unittest.main()

#### EOF ######################################################################
