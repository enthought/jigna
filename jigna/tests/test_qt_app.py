from jigna.api import QtApp
from jigna.api import Template

import unittest

class TestQtApp(unittest.TestCase):

    def test_widget_is_created(self):
        # Create a QtApp with an empty template and empty context
        template = Template(body_html="")
        app = QtApp(template=template, context={})

        # Create a widget
        widget = app.create_widget()

        # Check if the widget was created
        self.assertIsNotNone(widget)


if __name__ == "__main__":
    unittest.main()
