from traits.api import Dict, HasTraits, Instance, Int, Str, List, Event
from jigna.template import Template

import unittest
import time


def sleep_while(condition, timeout, dt=0.1):
    def _check_cond():
        try:
            return condition()
        except Exception:
            return True

    t = 0.0
    while _check_cond():
        time.sleep(dt)
        t += dt
        if t > timeout:
            return False
    return True



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
        print("JS: %s"%val)

    def method_slow(self, value, sleep_for):
        time.sleep(sleep_for)
        self.method_slow_called_with = value


class AddressBook(HasTraits):
    contacts = List

    def create(self):
        n = 10
        for i in range(n):
            self.contacts.append(Contact(name=str(i), number=str(i)))
        for i in range(n, 2*n):
            self.contacts.append(Company(
                name=str(i), number=str(i), address=str(i)
            ))


class Company(HasTraits):
    name = Str
    number = Str
    address = Str

class Contact(HasTraits):
    name = Str
    number = Str


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

    Spouse: <br/>
    Name: {{model.spouse.name}} Age: {{model.spouse.age}}

   <h3>Addressbook</h3>
   <button ng-click="jigna.threaded(addressbook, 'create')" id="create">
    Create
   </button>
   <br/>
   <ul>
    <li ng-repeat="contact in addressbook.contacts track by $index">
     <label>Name:</label> <input ng-model="contact.name">
     <label>Number:</label> <input ng-model="contact.number">
    </li>
   </ul>

"""

class TestJignaQt(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from jigna.qt import QtGui
        from jigna.html_widget import HTMLWidget
        from jigna.utils import gui
        qapp = QtGui.QApplication.instance() or QtGui.QApplication([])
        template = Template(body_html=body_html)
        fred = Person(name='Fred', age=42)
        addressbook = AddressBook()
        widget = HTMLWidget(
            template=template,
            context={'model':fred, 'addressbook': addressbook}
        )
        widget.show()
        gui.process_events()
        cls.widget = widget
        cls.fred = fred
        cls.addressbook = addressbook

    def setUp(self):
        cls = self.__class__
        self.widget = cls.widget
        self.fred = cls.fred
        self.fred.spouse = None
        self.fred.fruits = []
        self.fred.friends = []
        self.fred.called_with = None
        self.fred.method_slow_called_with = None
        self.addressbook = cls.addressbook

    def wait_and_assert(self, condition, timeout=1.0):
        self.assertTrue(sleep_while(condition, timeout=timeout))

    def execute_js(self, js):
        from jigna.utils import gui
        gui.process_events()
        result = self.widget.execute_js(js)
        gui.process_events()
        return result

    def process_events(self):
        from jigna.utils import gui
        gui.process_events()

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

    def test_object_identity(self):
        fred = self.fred
        wilma = Person(name='wilma')
        fred.friends.append(wilma)
        fred.spouse = wilma

        self.assertJSEqual(
            "jigna.models.model.friends[0] === jigna.models.model.spouse", True
        )

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
        sleep_while(lambda: fred.fruits[0] != 'orange', timeout=1.0)
        self.assertEqual(fred.fruits, ["orange", "peach", "pear", "mango"])

        self.execute_js("jigna.models.model.fruits = ['apple']")
        sleep_while(lambda: fred.fruits[0] != 'apple', timeout=1.0)
        self.assertEqual(fred.fruits, ["apple"])

    def test_list_slicing(self):
        fred = self.fred
        fred.fruits = ["peach", "pear", "banana", "fruit", "apple"]
        self.assertJSEqual("jigna.models.model.fruits", fred.fruits)

        # Test that deleting a single element works.
        del fred.fruits[3]
        self.assertJSEqual("jigna.models.model.fruits", fred.fruits)

        # Now try a complex slice.

        # Check if negative strides work.
        fred.fruits[::-2] = ["mango", "litchi"]
        self.assertJSEqual("jigna.models.model.fruits", fred.fruits)

        # Check if positive strides work.
        fred.fruits[::2] = ["mango", "litchi"]
        self.assertJSEqual("jigna.models.model.fruits", fred.fruits)

        # Now try deleting a slice
        del fred.fruits[::2]
        self.assertJSEqual("jigna.models.model.fruits", fred.fruits)

        fred.fruits = ["peach", "pear", "banana", "fruit", "apple"]
        del fred.fruits[::3]
        self.assertJSEqual("jigna.models.model.fruits", fred.fruits)

    def test_dict_of_primitives(self):
        self.assertJSEqual("jigna.models.model.phonebook", {})
        fred = self.fred
        fred.phonebook = {'joe' : 123, 'joan' : 345}
        self.assertJSEqual("jigna.models.model.phonebook.joe", 123)
        self.assertJSEqual("jigna.models.model.phonebook.joan", 345)
        self.assertJSEqual("jigna.models.model.phonebook", fred.phonebook)

        fred.phonebook['wilma'] = 678
        self.assertJSEqual("jigna.models.model.phonebook.wilma", 678)
        self.assertJSEqual(
            "Object.keys(jigna.models.model.phonebook).length", 3
        )

        fred.phonebook['wilma'] = 890
        self.assertJSEqual("jigna.models.model.phonebook.wilma", 890)
        self.assertJSEqual(
            "Object.keys(jigna.models.model.phonebook).length", 3
        )

        fred.phonebook.pop('wilma')
        self.assertJSEqual("jigna.models.model.phonebook.wilma", None)
        self.assertJSEqual(
            "Object.keys(jigna.models.model.phonebook).length", 2
        )

        # Test setting from the JS side...
        self.execute_js("jigna.models.model.phonebook['joe'] = 567")
        sleep_while(lambda: fred.phonebook['joe'] != 567, timeout=1.0)
        self.assertEqual(567, fred.phonebook['joe'])

        self.execute_js("jigna.models.model.phonebook = {'alan' : 987}")
        sleep_while(lambda: fred.phonebook != {'alan': 987}, timeout=1.0)
        self.assertEqual(fred.phonebook, {'alan': 987})

    def test_instance_trait(self):
        self.assertIn(self.execute_js("jigna.models.model.spouse"), ['', None])
        wilma = Person(name='Wilma', age=40)
        self.fred.spouse = wilma
        self.assertJSEqual("jigna.models.model.spouse.name", 'Wilma')
        self.assertJSEqual("jigna.models.model.spouse.age", 40)

        # Set in the JS side.
        self.execute_js("jigna.models.model.spouse.name = 'Wilmaji'")
        self.execute_js("jigna.models.model.spouse.age = 41")
        sleep_while(lambda: wilma.age != 41, timeout=1.0)
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
        sleep_while(lambda: barney.name != "Barneyji", timeout=1.0)
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

        sleep_while(lambda: fred.fruits[0] != 'apple', timeout=1.0)
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
        # Basically, we keep on checking for a condition which becomes true
        # when the function is finished, and raise an error if the timeout
        # occurs before the condition becomes true
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

    def test_nested_object_with_threaded_creation(self):
        # When

        # We trigger the click on setTimeout so as to avoid problems with
        # the JS code blocking any event processing
        self.execute_js(
            "setTimeout(function(){$('#create').trigger('click');});"
        )

        # Wait till the call is made.
        t = 0
        while len(self.addressbook.contacts) != 20 and t < 2.0:
            self.process_events()
            time.sleep(0.05)
            t += 0.05
        self.process_events()

        # Then.
        self.assertJSEqual('jigna.models.addressbook.contacts.length', 20)
        self.assertJSEqual('jigna.models.addressbook.contacts[1].name', '1')
        self.assertJSEqual('jigna.models.addressbook.contacts[1].number', '1')
        self.assertJSEqual('jigna.models.addressbook.contacts[10].name', '10')
        self.assertJSEqual('jigna.models.addressbook.contacts[10].number', '10')
        self.assertJSEqual('jigna.models.addressbook.contacts[10].address', '10')


if __name__ == "__main__":
    unittest.main()

#### EOF ######################################################################
