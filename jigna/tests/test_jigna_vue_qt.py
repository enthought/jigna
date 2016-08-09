from __future__ import absolute_import

import unittest

from .test_jigna_qt import Person, TestJignaQt, AddressBook

body_vue_html = """
    <div>
      Name: <input v-model="model.name">
      Age: <input v-model="model.age" number>
      <br/>
      Fruits:
      <ul>
        <li v-for="fruit in model.fruits" track-by="$index">
          <input v-model="fruit">
        </li>
      </ul>

      <br/>

      Friends:
      <ul>
        <li v-for="friend in model.friends">
          Name: <input v-model="friend.name">
          Age: <input v-model="friend.age" number>
          Fruits:
          <ul>
            <li v-for="fruit in friend.fruits">
              <input v-model="fruit">
            </li>
          </ul>
        </li>
      </ul>
    </div>

    Spouse: <br/>
    Name: {{model.spouse.name}} Age: {{model.spouse.age}}

   <h3>Addressbook</h3>
   <button v-on:click="threaded(addressbook, 'create')" id="create">
    Create
   </button>
   <br/>
   <ul>
    <li v-for="contact in addressbook.contacts">
     <label>Name:</label> <input v-model="contact.name">
     <label>Number:</label> <input v-model="contact.number">
    </li>
   </ul>
"""

class TestJignaVueQt(TestJignaQt):

    @classmethod
    def setUpClass(cls):
        from jigna.api import HTMLWidget, VueTemplate
        from jigna.utils import gui
        from jigna.qt import QtGui
        qapp = QtGui.QApplication.instance() or QtGui.QApplication([])
        template = VueTemplate(body_html=body_vue_html)
        fred = Person(name='Fred', age=42)
        addressbook = AddressBook()
        widget = HTMLWidget(
            template=template,
            context={'model':fred, 'addressbook': addressbook})
        widget.show()
        gui.process_events()
        cls.widget = widget
        cls.fred = fred
        cls.addressbook = addressbook

del TestJignaQt

if __name__ == "__main__":
    unittest.main()
