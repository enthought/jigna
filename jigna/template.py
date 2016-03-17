#
# Enthought product code
#
# (C) Copyright 2013-2016 Enthought, Inc., Austin, TX
# All right reserved.
#

from textwrap import dedent

# Enthought library.
from traits.api import Bool, HasTraits, Str, Property, Tuple, Int


#### HTML template ############################################################

class Template(HasTraits):
    """ Encapsulation of the HTML/AngularJS template which can be rendered by
    jigna.
    """

    #### 'Template' protocol ##################################################

    #: Should we use the async client or not.
    #:
    #: Async client presents a deferred API and is useful when you want to have
    #: your View served over the web where you don't want to freeze the browser
    #: during synchronous GET calls from the server.
    #:
    #: NOTE: When you're specifying the full HTML for the View, the option to
    #: start an async client is specified at the Javascript level instead of
    #: here, using the Javascript statement: `jigna.initialize({async: true})`.
    #: In that case, the value of this trait becomes moot.
    async = Bool(False)

    #: The base url for all resources (relative urls are resolved corresponding
    #: to the current working directory).
    base_url = Str

    #: The inner HTML for the *body* of the view's document.
    body_html = Str

    #: The inner HTML for the *head* of the view's document.
    head_html = Str

    #: The file which contains the html. `html_file` takes precedence over
    #: `body_html` and `head_html`.
    html_file = Str

    #: The HTML template used for this.
    html_template = Str

    #: The HTML for the entire document.
    #:
    #: The order of precedence in determining its value is:
    #:  1. Directly specified `html` trait
    #:  2. Read the contents of the file specified by the `html_file` trait
    #:  3. Create the jigna template out of specified `body_html` and `head_html`
    #:     traits
    html = Property(Str)
    _html = Str

    #: Recommended size of the HTML (in a (width, height) format)
    recommended_size = Tuple(Int(600), Int(400))

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
            html = self.html_template.format(
                body_html = self.body_html,
                head_html = self.head_html,
                async     = async,
            )

        return html

    def _set_html(self, html):
        self._html = html

    def _html_template_default(self):
        return dedent("""
        <html ng-app='jigna'>
          <head>
            <script type="text/javascript" src="/jigna/jigna.js"></script>
            <script type="text/javascript">
                jigna.initialize({{async: {async}}});
            </script>

            {head_html}

          </head>

          <body>
            {body_html}
          </body>

        </html>
        """)
