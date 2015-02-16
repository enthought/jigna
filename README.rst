Jigna
=====

Jigna is a bridge between Traits and the HTML world to provide a UI toolkit for
traits models that is based on the powerful technologies of HTML, CSS and
Javascript.

It provides two-way data bindings between the traits model and the HTML
interface i.e. traits notifications automatically update the HTML UI and user
inputs on the UI seamlessly change model attributes in Python. Jigna uses
AngularJS for data bindings and one could think of it as an equivalent of
AngularJS where the model lives in Python instead of Javascript. This gives us
the power of Python and Traits for easily writing the application logic and the
flexibility and expressibility of HTML for the user interface.

The HTML UI can be displayed both in the same Python process as well as
remotely, allowing us to view and manipulate a Traits-based-object from the web.

Installation
============

These installation instructions assume that you have a working Python
environment with enpkg and pip installed in it.

The standard installation installs a PySide based Qt egg for displaying the UI::

    enpkg traits pyside
    python setup.py develop

If you want a PyQt based installation, you can install PyQt from pip::

    enpkg traits
    pip install python-qt
    python setup.py develop

If you want a web based installation (for viewing the UI in a regular web
browser), you need to install tornado::

    enpkg traits tornado
    python setup.py develop

Testing
=======

For testing the library, you need to install some additional dependencies::

    pip install nose selenium coverage

To run the tests, you can simply do the following from the project's root
directory::

    nosetests

Examples
========

There are several examples to play with in the ``examples`` directory. Each
example demonstrates one particular feature of jigna. Start with the simplest
one by running::

    python simple_view.py
