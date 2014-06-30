#
# Enthought product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#

# Enthought library.
from traits.api import HasTraits, Instance, Dict

# Jigna libary.
from jigna.api import Template
from jigna.server import Server

class View(HasTraits):
    """ An abstract class to represent a jigna view. """

    #### 'View' protocol ######################################################

    #: The jigna template object which contains the HTML template and the JS
    #: code to bind it to Python domain models.
    template = Instance(Template)

    #: The context which is used to render the template. This is a dict of
    #: name-object pairs where the name specifies the name used in the template
    #: to refer to an object.
    context = Dict

    def start(self):
        """
        The (usually) blocking call to start the view.
        """
        raise NotImplementedError

    #### Private protocol #####################################################

    #: The server that manages the objects shared via the bridge.
    _server = Instance(Server)
