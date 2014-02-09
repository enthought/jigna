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


Examples
---------

There are several examples to get started, look in the ``examples/`` directory
and run them.

Tests
------

Running the tests requires selenium_ and nose_.  The tests are in
``jigna/tests/``.  You may run them from the root directory of the sources
using ``nosetests``.

.. _selenium: https://pypi.python.org/pypi/selenium
.. _nose: https://pypi.python.org/pypi/nose


Getting started
----------------

Let us say we have a nice model written in Python (specifically, in Traits_)::

    from traits.api import HasTraits, Str

    class Model(HasTraits):
        name = Str
        greeting = Str
        def _name_changed(self):
            self.greeting = "Hello " + self.name

    model = Model(name='Fred')

We would like to write simple HTML to visualize this and have the model and
view be fully connected. Here is a sample HTML (an AngularJS_ template)::

    body_html = """
   	Name: <input ng-model="model.name"/><br>
   	Greeting:
   	<h1>{{model.greeting}}</h1>
    """

Notice how the HTML is directly referencing model attributes via model.name
and model.greeting. We now bind this declarative view to the model and create
a Qt based UI::

    from jigna.api import View
    person_view = View(body_html=body_html)

    from PySide import QtGui
    app = QtGui.QApplication([])
    person_view.show(model=model)
    app.exec_()

This produces an HTML UI which responds automatically to any changes in the
model and vice-versa. It can optionally be styled with CSS and made
interactive with Javascript. Clearly the above example is a toy example, but
this shows a nice way of easily building rich, live user interfaces for Python
apps.

This is nice for several reasons:

 * The view code is declarative and hence easy to read.

 * The binding between the model and the view is automatic.

 * HTML/CSS/JS today is very powerful

   - there are many JS libraries for a variety of tasks

   - your development team doesn't have to worry about creating widgets or the
     limitations in the toolkit’s widget set as there are thousands of
     developers worldwide creating awesome CSS/JS widgets for you.

 * Much easier to find people who know HTML/CSS/JS than Qt or a native toolkit.

 * There is a complete separation of view from the model and this allows us to
   hand off the entire UI to an HTML/CSS/JS guru.

And if this were not enough, the view can also be easily served on a web
browser if we just did the following::

    person_view.serve(model=model)

This starts up a web server to which one can connect multiple browsers to see
and interact with the model.

.. _AngularJS: http://angularjs.org/


How is this different from just HTML rendered via webkit?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For a simple Python desktop application, it is relatively easy to create an
HTML view using a webkit browser widget.  However, the connection between the
model and the HTML UI can be involved resulting in fairly complicated code.
Most web frameworks provide this functionality but are web-centric, and are
centered around building web applications, not desktop applications.

Our goal is to be able to build a desktop UI completely in HTML where the HTML
template always remains live by referring directly to Python object attributes
and methods. Changes in the Python side should update the UI and user inputs
on the UI should be able to update the model. Also, we need to have clear
separation between the view and the model. Jigna provides us this capability.


How it works
~~~~~~~~~~~~~

It turns out that Qt's ``QtWebkit`` browser has support for in-process
communication between its Javascript engine and the running Python
application. We use this communication channel to create a Javascript proxy
for Python models.

The other nice piece in this story is AngularJS, which provides good
model-view separation between its HTML template and the corresponding
Javascript model. AngularJS has great support for two-way data binding between
the template and the model, which keeps the template expressions always in
sync with the JS model. This makes sure that the HTML you need to write is
terse and simple.

We combine these two pieces to create a lazy-loaded Python-JS bridge which
provides us the two-way data binding between the Python model and the HTML
view. We use Traits to write models in Python. Traits lets us define
attributes of an object statically, and supports notifications when the
attributes change. Jigna integrates well with traits so that these
notifications automatically update the UI. Similarly, user inputs on the UI
change model attributes, call public methods on the model as well. Note
however that you don’t need traits and you can bind it to your plain old
Python objects as well - you would just need to add your own events if you
want your models to be updated outside of the UI.
