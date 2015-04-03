from traits.api import Dict, HasTraits, Instance, Int, Str, List, Event
from jigna.api import HTMLWidget, Template
from jigna.utils import gui
from jigna.qt import QtGui

import unittest
import time

#### Test model ####

class Person(HasTraits):
    name = Str
    age  = Int
    spouse = Instance('Person')
    fruits = List(Str)
    friends = List(Instance('Person'))
    phonebook = Dict(Str, Int)

    name_updated = Event

    def method(self, value):
        self.called_with = value

    def printme(self, val):
        print "JS:", val

    def method_slow(self, value, sleep_for):
        time.sleep(sleep_for)
        self.method_slow_called_with = value

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

    Spouse: {{model.spouse}}
"""

class TestJignaQt(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        qapp = QtGui.QApplication.instance() or QtGui.QApplication([])
        template = Template(body_html=body_html)
        fred = Person(name='Fred', age=42)
        widget = HTMLWidget(template=template, context={'model':fred})
        widget.show()
        gui.process_events()
        cls.widget = widget
        cls.fred = fred

    def setUp(self):
        cls = self.__class__
        self.widget = cls.widget
        self.fred = cls.fred
        self.fred.spouse = None
        self.fred.fruits = []
        self.fred.friends = []
        self.fred.called_with = None
        self.fred.method_slow_called_with = None

    def execute_js(self, js):
        gui.process_events()
        result = self.widget.execute_js(js)
        gui.process_events()
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
        self.assertJSEqual("jigna.models.model.name", fred.name)
        fred.age = 43
        self.assertJSEqual("jigna.models.model.age", fred.age)

    def test_list_of_primitives(self):
        self.assertJSEqual("jigna.models.model.fruits", [])
        fred = self.fred
        fred.fruits = ["peach", "pear"]
        self.assertJSEqual("jigna.models.model.fruits", fred.fruits)

        fred.fruits.append('mango')
        self.assertJSEqual("jigna.models.model.fruits[0]", "peach")
        self.assertJSEqual("jigna.models.model.fruits[1]", "pear")
        self.assertJSEqual("jigna.models.model.fruits[2]", "mango")

        fred.fruits.insert(0, 'banana')
        self.assertJSEqual("jigna.models.model.fruits[0]", "banana")
        self.assertJSEqual("jigna.models.model.fruits[1]", "peach")
        self.assertJSEqual("jigna.models.model.fruits[2]", "pear")
        self.assertJSEqual("jigna.models.model.fruits[3]", "mango")
        
        # Test setting from the JS side...
        self.execute_js("jigna.models.model.fruits[0] = 'orange'")
        self.assertEqual(fred.fruits, ["orange", "peach", "pear", "mango"])

        self.execute_js("jigna.models.model.fruits = ['apple']")
        self.assertEqual(fred.fruits, ["apple"])

    def test_dict_of_primitives(self):
        self.assertJSEqual("jigna.models.model.phonebook", {})
        fred = self.fred
        fred.phonebook = {'joe' : 123, 'joan' : 345}
        self.assertJSEqual("jigna.models.model.phonebook.joe", 123)
        self.assertJSEqual("jigna.models.model.phonebook.joan", 345)
        self.assertJSEqual("jigna.models.model.phonebook", fred.phonebook)

        # Now set the value in the JS side.
        self.execute_js("jigna.models.model.phonebook['joe'] = 567")
        self.assertEqual(567, fred.phonebook['joe'])

        self.execute_js("jigna.models.model.phonebook = {'alan' : 987}")
        self.assertEqual(fred.phonebook, {'alan' : 987})

    def test_instance_trait(self):
        self.assertIn(self.execute_js("jigna.models.model.spouse"), ['', None])
        wilma = Person(name='Wilma', age=40)
        self.fred.spouse = wilma
        self.assertJSEqual("jigna.models.model.spouse.name", 'Wilma')
        self.assertJSEqual("jigna.models.model.spouse.age", 40)

        # Set in the JS side.
        self.execute_js("jigna.models.model.spouse.name = 'Wilmaji'")
        self.execute_js("jigna.models.model.spouse.age = 41")
        self.assertEqual(wilma.name, "Wilmaji")
        self.assertEqual(wilma.age, 41)

    def test_list_of_instances(self):
        self.assertJSEqual("jigna.models.model.friends", [])
        dino = Person(name="Dino", age=10)
        fred = self.fred
        fred.friends = [dino]
        self.assertJSEqual("jigna.models.model.friends[0].name", "Dino")
        self.assertJSEqual("jigna.models.model.friends[0].age", 10)

        wilma = Person(name="Wilma", age=30)
        fred.friends.append(wilma)
        self.assertJSEqual("jigna.models.model.friends[0].name", "Dino")
        self.assertJSEqual("jigna.models.model.friends[0].age", 10)
        self.assertJSEqual("jigna.models.model.friends[1].name", "Wilma")
        self.assertJSEqual("jigna.models.model.friends[1].age", 30)

        barney = Person(name="Barney", age=40)
        fred.friends.insert(0, barney)
        self.assertJSEqual("jigna.models.model.friends[0].name", "Barney")
        self.assertJSEqual("jigna.models.model.friends[0].age", 40)
        self.assertJSEqual("jigna.models.model.friends[1].name", "Dino")
        self.assertJSEqual("jigna.models.model.friends[1].age", 10)
        self.assertJSEqual("jigna.models.model.friends[2].name", "Wilma")
        self.assertJSEqual("jigna.models.model.friends[2].age", 30)

        # Test setting from the JS side...
        self.execute_js("jigna.models.model.friends[0].name = 'Barneyji'")
        self.assertEqual(barney.name, "Barneyji")

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

        # Then
        self.assertJSEqual(
            "jigna.models.model.fruits", ['apple', 'banana', 'peach']
        )
        self.assertEqual(fred.fruits, ['apple', 'banana', 'peach'])

    def test_callable(self):
        fred = self.fred
        wilma = Person(name='Wilma', age=40)
        self.fred.spouse = wilma
        self.execute_js("jigna.models.model.method('hello')")
        self.assertEqual(fred.called_with, "hello")
        self.execute_js("jigna.models.model.method(1)")
        self.assertEqual(fred.called_with, 1)
        self.execute_js("jigna.models.model.method(10.0)")
        self.assertEqual(fred.called_with, 10.0)
        self.execute_js("jigna.models.model.method([1,2])")
        self.assertEqual(fred.called_with, [1,2])
        self.execute_js("jigna.models.model.method(jigna.models.model.spouse)")
        self.assertEqual(fred.called_with, wilma)

    def test_events_js(self):
        # When
        self.execute_js("""
            jigna.add_listener(jigna.models.model, 'name_updated', function(event){
                jigna.models.model.new_name = event.data.value;
            })
        """)
        self.fred.name_updated = "Freddie"

        # Then
        self.assertJSEqual("jigna.models.model.new_name", "Freddie")

    def test_threaded_call(self):
        # When
        self.execute_js("""
            var deferred = jigna.threaded(jigna.models.model, 'method_slow', 'foo', 1);
            deferred.done(function(){
                jigna.models.model.method_slow_finished = true;
            })
        """)

        # The following is a way to test async methods.
        # Basically, we keep on checking for a condition which becomes true when
        # the function is finished, and raise an error if the timeout occurs before
        # the condition becomes true
        timeout = 1.5
        dt = 0.1
        for i in range(int(timeout/dt)):
            time.sleep(dt)
            try:
                self.assertJSEqual('jigna.models.model.method_slow_finished', True)
                self.assertEqual(self.fred.method_slow_called_with, 'foo')
                break
            except Exception:
                pass
        else:
            raise AssertionError("Async method not finished")

if __name__ == "__main__":
    unittest.main()

#### EOF ######################################################################
