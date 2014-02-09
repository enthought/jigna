Introduction
=============

Jigna aims to provide an HTML based solution for creating beautiful user
interfaces for Python applications, as opposed to widget based toolkits like
Qt/wx or native toolkits. It provides a seamless two-way data binding between
the Python model and the HTML view by creating a Python-JS communication
bridge. This ensures that the view is always live as it can automatically
update itself when the model changes, and update the model when user actions
take place on the UI. The Jigna view can be rendered in an in-process Qt
widget or over the web in a browser.


Installation
-------------

Jigna currently only works with Python-2.x, 3.x is not yet supported. You will
require the following packages installed:

 * You will need to have Traits_ installed to use Jigna.

 * Jigna can be used either as part of a Qt application or can be used to
   display a user interface on a web browser.  If you are only interested in
   using Jigna in a Qt-based application, you will also require pyface_.

 * If you need to use the web backend, you will require Tornado_.


.. _Traits: https://github.com/enthought/traits
.. _pyface: https://github.com/enthought/pyface
.. _Tornado: http://www.tornadoweb.org/en/stable/


Installation itself is standard and can be done from source via either::

    $ python setup.py install # or
    $ python setup.py develop
