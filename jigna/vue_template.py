#
# Enthought product code
#
# (C) Copyright 2013-2016 Enthought, Inc., Austin, TX
# All right reserved.
#

# Enthought library.
from traits.api import Str
from template import Template


DOCUMENT_VUE_HTML_TEMPLATE = """
<html>
  <head>
    <script type="text/javascript" src="/jigna/jigna-vue.js"></script>
    {head_html}
  </head>

  <body>
    {body_html}
  </body>

  <script type="text/javascript">
      var vm = undefined;
      // jigna.models are ready only when the deferred returned by initialize
      // is resolved. One could also use jigna.ready.done.
      jigna.initialize({{async: {async}}}).done(function() {{
          vm = new Vue({{
              el: 'body',
              data: jigna.models
          }});
      }});
  </script>

  {foot_html}
</html>
"""

class VueTemplate(Template):
    """A template for vue.js templates.  Note that this assumes that the
    ViewModel is attached to the body and all the jigna models are exposed.
    """
    #: The foot HTML for the *head* of the view's document.
    foot_html = Str

    def _get_html(self):
        """ Get the default HTML document for the given model. """

        # Return the cached html value if the trait is specified directly
        if len(self._html) > 0:
            return self._html

        # Else, read from the html file if it is specified...
        if len(self.html_file) > 0:
            with open(self.html_file) as f:
                html = f.read()

        # ...otherwise, create the template out of body and head htmls
        else:
            async = 'true' if self.async else 'false'
            html = DOCUMENT_VUE_HTML_TEMPLATE.format(
                body_html = self.body_html,
                head_html = self.head_html,
                foot_html = self.foot_html,
                async     = async,
            )

        return html
