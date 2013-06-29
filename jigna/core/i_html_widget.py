#
# Jigna product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX  
# All right reserved.  
#
# This file is confidential and NOT open source.  Do not distribute.
#

# Enthought library imports.
from pyface.i_widget import IWidget
from traits.api import HasTraits, Bool, Callable, Dict, Either, Event, \
    Instance, List, Str, Tuple, Unicode, Float, Any


class IHTMLWidget(IWidget):
    """ A widget for displaying web content.

    The widget has support for HTML rendering, URL navigation, and
    Python-Javascript interoperation.
    """
    
    #### 'IHTMLWidget' interface ##############################################

    # The URL for the current page. Read only.
    url = Str

    # Whether the page is currently loading.
    loading = Bool

    # Fired when the page has completely loaded.
    loaded = Event

    # The title of the current web page.
    title = Unicode

    # Should links be opened in an external browser? Note that any custom URL
    # handling takes precedence over this option.
    open_externally = Bool(False)

    # The zoom level of the page
    zoom = Float(1)

    # Additional JavaScript to be executed after the page load finishes.
    post_load_js = List(Str)

    # Whether debugging tools are enabled in the web view.
    debug = Bool

    #### Python-JavaScript interoperation #####################################

    # The object to expose to JavaScript using the information below. Optional.
    js_object = Instance(HasTraits)

    # A list of callables to expose to Javascript. Each pair is either a method
    # name or a tuple of form:
    #
    #     (javascript_name, callable(arg1, arg2, ...) -> result).
    #
    # Only primitive values (bool, int, long, float, str, and unicode) are
    # supported as arguments and return values. Keyword arguments and
    # variable-length argument lists are ignored.
    callbacks = List(Either(Str, Tuple(Str, Callable)))

    # A list of schemes to intercept clicks on, and functions to
    # handle them, e.g.
    #
    #     ('doc', foo.open_doc)
    #
    # The callback should take a URL and handle opening or loading.
    click_schemes = Dict(Str, Callable)

    # A list of hosts and wsgi apps to handle them
    # (http://www.python.org/dev/peps/pep-3333/), e.g., 
    #
    #     ('doc.jigna', doc_url_to_html)
    #
    # The callback should take a URL and return an HTML string.
    hosts = Dict(Str, Callable)

    # A list of traits to expose to Javascript. Each item is a either a trait
    # name or a tuple of form:
    #
    #     (javascript_name, trait_name)
    #
    # Only structures consisting of lists, dicts, and primitive values (bool,
    # int, long, float, str, and unicode) are supported.
    properties = List(Either(Str, Tuple(Str, Str)))

    # The name of the Javascript object that will contain the registered
    # callbacks and properties.
    python_namespace = Str('python')

    #### Advanced Python-Javascript interoperation ############################

    # Provides advanced Python-Javascript interoperation. Any handlers defined
    # here take precedence over the simplified API above. See
    # ``WebAccessManager`` for documentation.
    access_manager = Any
    
    ###########################################################################
    # 'IHTMLWidget' interface.
    ###########################################################################

    def create(self, parent=None):
        """ Create the HTML widget's underlying control.

        The HTML widget should be torn down by calling ``destroy()``, which is
        part of the IWidget interface.
        """

    def execute_js(self, js):
        """ Execute JavaScript synchronously.

        Warning: under most circumstances, this method should not be called when
        the page is loading.
        """

    def load_html(self, html, base_url=None):
        """ Loads raw HTML into the widget.

        Parameters:
        -----------
        html : unicode
            An HTML string.

        base_url : str
            If specified, external objects (e.g. stylesheets and images) are
            relative to this URL.
        """

    def load_url(self, url):
        """ Loads the given URL.
        """

    #### Navigation ###########################################################

    def back(self):
        """ Navigate backward in history.
        """

    def forward(self):
        """ Navigate forward in history.
        """
        
    def reload(self):
        """ Reload the current web page.
        """
        
    def stop(self):
        """ Stop loading the curent web page.
        """

    #### Generic GUI methods ##################################################

    def undo(self):
        """ Performs an undo action in the underlying widget.
        """

    def redo(self):
        """ Performs a redo action in the underlying widget.
        """

    def cut(self):
        """ Performs a cut action in the underlying widget.
        """

    def copy(self):
        """ Performs a copy action in the underlying widget.
        """

    def paste(self):
        """ Performs a paste action in the underlying widget.
        """

    def select_all(self):
        """ Performs a select all action in the underlying widget.
        """
