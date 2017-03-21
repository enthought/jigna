#
# Enthought product code
#
# (C) Copyright 2013-2016 Enthought, Inc., Austin, TX
# All right reserved.
#

from textwrap import dedent

# Local imports
from .template import Template


class VueTemplate(Template):
    """A template for vue.js templates.  Note that this assumes that the
    ViewModel is attached to the body and all the jigna models are exposed.
    """
    def _html_template_default(self):
        return dedent("""
        <html>
          <head>
            <script type="text/javascript" src="/jigna/jigna-vue.js"></script>
            {head_html}
          </head>

          <body>
            {body_html}

          <script type="text/javascript">
              var vm = undefined;
              // jigna.models are ready only when the deferred returned by initialize
              // is resolved. One could also use jigna.ready.done.
              jigna.initialize({{async: {async}}}).done(function() {{
                  vm = new Vue({{
                      el: 'body',
                      data: jigna.models,
                      methods: {{
                        threaded: function(obj, method_name, args) {{
                           jigna.threaded.apply(jigna, arguments);
                        }},
                      }}
                  }});
              }});
          </script>
          </body>

        </html>
        """)
