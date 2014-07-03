"""
Utility methods for the IPython notebook
"""

from jigna.api import WebApp
import threading

app = None

def display_jigna(context, template):
    """
    A `display_html` style method to show rich jigna display for the objects
    within the context.
    """
    global app

    if not app:
        app = WebApp(context=context, template=template, port=8005)
        t = threading.Thread(target=app.start)
        t.start()

    else:
        # Update the context being served on the web app
        app.update_context(context=context)

    from IPython.display import Javascript

    # The Javascript code to compile the template which is added dynamically to
    # the DOM
    js = """
        console.log('jigna loaded', element);
        var injector = angular.inject(['ng']);
        var $compile = injector.get('$compile');
        var $scope = $(document.body).scope();

        console.log('compiling');
        var linkFn = $compile('%s');
        console.log('compiled');
        var new_element = linkFn($scope);

        // 'element' is exposed by IPython notebook to refer to the cell's
        // output area element
        $(element).append(new_element);

        // Fire a $digest cycle so that the template is updated with the latest
        // values
        $scope.$digest();
    """ % template.body_html

    print js

    return Javascript(js, lib='http://localhost:8005/jigna/jigna.js')
