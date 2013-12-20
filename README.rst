About Jigna
============

Jigna is a bridge between Traits and the HTML world to provide a UI toolkit for
traits models that is based on the powerful technologies of HTML, CSS and Javascript.
It provides two-way data bindings between the traits model and the HTML interface
i.e. traits notifications automatically update the HTML UI and user inputs on
the UI seamlessly change model attributes in Python. Jigna uses AngularJS for
data bindings and one could think of it as an equivalent of AngularJS where the
model lives in Python instead of Javascript. This gives us the power of Python and
Traits for easily writing the application logic and the flexibility and expressibility
of HTML for the user interface.

The HTML UI can be displayed both in the same Python process as well as remotely, 
allowing us to view and manipulate a Traits-based-object from the web.


Installation
=============

You will require the following packages:

 - Traits.
 - Pyface with a working Qt backend (either PySide or PyQt4).

For the web interface, you need:

 - Tornado.

You can install this either via pip or the usual means::

    python setup.py install
    python setup.py develop

or::

    pip install -r requirements.txt


Examples
=========

If you have set `ETS_TOOLKIT`, remember to set it to `qt4`.  There are
several examples to play with in the `examples` directory.
