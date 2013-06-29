# Standard library imports
from mako.template import Template

# Enthought library imports
from pyface.qt import QtGui

# Local imports
from jigna.core.html_widget import HTMLWidget
from jigna.templates import html, js
from jigna.util import serialize
from jigna.util.wsgi import JinjaRenderer

class HTMLView(object):
    
    def __init__(self, model):
        self.model = model
        self._resource_host = 'resources.jigna'
        self._resource_url = "http://{0}/".format(self._resource_host)
        
    def generate_html_js_css(self):
        self.js = js.to_js(obj=self.model)
        self.css = ""
        self.html = html.to_html(obj=self.model, js=self.js, css=self.css, 
                                 resource_url=self._resource_url)
    
    def _create_widget(self):
        hosts = {self._resource_host: JinjaRenderer(
                    package='jigna',
                    template_root='resources'
                    )}
        self.widget = HTMLWidget(callbacks=[('trait_set', self.trait_set)],
                                 python_namespace='pyobj_%s'%id(self.model), 
                                 hosts=hosts,
                                 open_externally=True,
                                 debug=True
                                 )
        self.widget.create()
        
    def _bind_trait_change_events(self):
        def handler(model, tname, oldValue, newValue):
            template = Template("""
                                scope = $('#id_${id(obj)}').scope();
                                scope.scoped(function() {
                                    scope.${tname} = JSON.parse('${value}');
                                })
                                """)
            traitchange_js = template.render(obj=self.model, tname=tname, 
                                             value=serialize(newValue))
            self.widget.execute_js(traitchange_js)

        self.model.on_trait_change(handler)
        
    def trait_set(self, tname, value):
        setattr(self.model, tname, value)
    
    def show(self):
        self.generate_html_js_css()
        app = QtGui.QApplication.instance() or QtGui.QApplication([])
        self._create_widget()
        self._bind_trait_change_events()
        self.widget.load_html(self.html)
        self.widget.control.show()
        app.exec_()
    