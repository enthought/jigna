About Jigna
============

Jigna is a TraitsUI like frontend for Traits, but unlike TraitsUI which is
based on Qt/Wx, it is based on HTML/CSS/JS.   One could think of Jigna as a
HTML backend for TraitsUI.  Jigna allows us to develop models in Python but
create a user interface using HTML/CSS/JS. This gives us the power of Python
for easily writing the application logic and the powerful features of the HTML
world for the user interface. The HTML UI can be displayed both in the same
Python process as well as remotely, allowing us to view and manipulate a
Traits-based-object seamlessly from the web.

For the in-process implementation one requires PySide or PyQt and we rely on
Qt-Webkit support to do this.

For the web interface we require tornado.


Installation
=============

You will require the following packages:

 - Traits.
 - TraitsUI.
 - Pyface.
 - Working Qt backend for Traits (either PySide or PyQt4).
 - Mako and Jinja2.
 - BeautifulSoup4.
 - Tornado for the websocket implementation.

You can install this either via pip or the usual means::

    python setup.py install
    python setup.py develop

or::

    pip install -r requirements.txt


Examples
=========

If you have set `ETS_TOOLKIT`, remember to set it to `qt4`.  There are
several examples to play with in the `examples` directory.
