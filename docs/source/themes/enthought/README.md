Enthought Sphinx Theme
======================
This project is a derivative of Ryan Roemer's [Sphinx Bootstrap Theme] (https://github.com/ryan-roemer/sphinx-bootstrap-theme).

Intallation
-----------
To install theme Enthought, copy the whole of ```enthought``` directory into 
the ```themes``` directory in your Sphinx source directory. If ``themes`` does 
not exist, create a new one.

You may have a different directory in your Sphinx source where you install your
themes; use the existing location to copy ```enthought``` Sphinx theme if it
exits.

The theme uses ```source/_static/logo.png``` as the logo in the header by default. 
You may either copy your logo image to this location or change the relevant path
to image file in [```source/themes/enthought/layout.html```] (https://github.com/enthought/sphinx-theme/blob/316a9e49d1a59459af1b7b53aef91cf8b720475b/enthought/layout.html#L20)

Configuration changes
---------------------
Add the following to your Sphinx configuration file ```conf.py```:

```
sys.path.append(os.path.abspath('themes'))

html_theme = 'enthought'
html_theme_path = ['themes']
html_theme_options = {
    'navbar_fixed_top': "false",
}
```

