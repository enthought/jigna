from jigna.api import HTMLWidget, VueTemplate
from jigna.utils import gui
from jigna.qt import QtGui

import unittest

from test_jigna_qt import Person, TestJignaQt

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

    Spouse: {{model.spouse}}
"""

class TestJignaVueQt(TestJignaQt):

    @classmethod
    def setUpClass(cls):
        qapp = QtGui.QApplication.instance() or QtGui.QApplication([])
        template = VueTemplate(body_html=body_vue_html)
        fred = Person(name='Fred', age=42)
        widget = HTMLWidget(template=template, context={'model':fred})
        widget.show()
        gui.process_events()
        cls.widget = widget
        cls.fred = fred

del TestJignaQt

if __name__ == "__main__":
    unittest.main()
