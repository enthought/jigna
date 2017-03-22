Jigna
=====

.. image:: https://travis-ci.org/enthought/jigna.svg?branch=master
    :target: https://travis-ci.org/enthought/jigna
    :alt: Travis-CI build status

.. image:: https://ci.appveyor.com/api/projects/status/71v3yq4becmwj6fk?svg=true
    :target: https://ci.appveyor.com/project/Enthought/jigna
    :alt: Appveyor build status

.. image:: https://codecov.io/gh/enthought/jigna/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/enthought/jigna
    :alt: Codecov status

.. image:: https://readthedocs.org/projects/jigna/badge/?version=latest
    :target: http://jigna.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status


Jigna is a bridge between Traits_ and the HTML world to provide a UI toolkit for
traits models based on the powerful technologies of HTML, CSS and Javascript.

It provides two-way data bindings between the traits model and the HTML
interface i.e. traits notifications automatically update the HTML UI and user
inputs on the UI seamlessly change model attributes in Python. Jigna uses
AngularJS_ (or `Vue.js`_) for data bindings and one could think of it as an
equivalent of AngularJS where the model lives in Python instead of Javascript.
This gives us the power of Python and Traits for easily writing the application
logic and the flexibility and expressibility of HTML for the user interface.

The HTML UI can be displayed both in the same Python process as well as
remotely, allowing us to view and manipulate a Traits-based-object from the web.

Jigna can be used to create user interfaces in Qt using Qt's webkit support or
on a browser. One needs to have Qt (PySide or PyQt) installed if one wants a Qt
based UI and requires tornado_ for a web-based UI.

With a web-based UI, the jigna dependencies are rather light requiring only
traits, tornado, and a recent web browser.

Please note that Jigna currently is only tested with Qt4 and Qt5 support will be
added later.


.. _Traits: http://code.enthought.com/projects/traits/
.. _tornado: http://tornadoweb.org
.. _AngularJS: http://angularjs.org
.. _`Vue.js`: http://vuejs.org


Installation
============

Jigna can be installed with ``pip``::

    $ pip install jigna

This will not pull in any Qt requirements but will require tornado_ as it is
easy to install.  The test requirements can be installed via::

    $ pip install jigna[test]

This will install, PySide, nose, mock, coverage, and selenium_ if you do not
already have them.

To install Jigna from the sources you may do the following::

    git clone git@github.com:enthought/jigna.git
    cd jigna
    pip install -r requirements.txt
    python setup.py install # or python setup.py develop

This does not include pyside or pyqt so you will have to install that as well.

.. _selenium: https://pypi.python.org/pypi/selenium


Testing
=======

To run the tests, you can simply do the following from the project's root
directory::

    nosetests

You must make sure you have the required packages installed, and can install
these via::

    pip install -r requirements.txt

This does not install pyside since that is a heavy dependency. You may install
it using your package manager or via pip.

Examples
========

There are several examples to play with in the ``examples`` directory. Each
example demonstrates one particular feature of jigna. Start with the simplest
one by running::

    python ex1_simple_view.py

This requires Qt so if you are only interested in Web UI examples, you may run
the following examples:

- ``ex3_simple_view_web.py``
- ``ex7_model_updates_web.py``
- ``ex20_mayavi_webgl_demo.py`` -- this requires Mayavi to be installed.
