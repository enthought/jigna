# Standard library imports
from textwrap import dedent
from mako.template import Template

# Enthought library imports
from pyface.qt import QtWebKit, QtGui
from traitsui.api import View, Item
from enable.component_editor import ComponentEditor

from jigna.editors.basic_editors import BasicEditor
import jigna.registry as registry

class ChacoWidget(QtGui.QWidget):
    def __init__(self, model_id):
        super(ChacoWidget, self).__init__()
        self.model_id = model_id
        self.model = registry.registry['models'][self.model_id]
        l = QtGui.QVBoxLayout()
        self.setLayout(l)
        self.show()
        self.setMinimumWidth(800)
        self.setMinimumHeight(700)
        e = self.model.edit_traits(view=View(Item('plot', style='custom', show_label=False,
                                             editor=ComponentEditor()),
                                             width=800, height=700),
                                             parent=self,
                                             kind='subpanel')
        l.addChildWidget(e.control)

class ChacoWidgetFactory(QtWebKit.QWebPluginFactory):

    MIME_TYPE = "application/x-chacowidget"

    def __init__(self, webview):
        super(ChacoWidgetFactory, self).__init__(webview)
        self.webview = webview

    def plugins(self):
        plugin = QtWebKit.QWebPluginFactory.Plugin()
        plugin.name = "ChacoWiget"
        plugin.description = "Embedded chaco widget"
        mimeType = QtWebKit.QWebPluginFactory.MimeType()
        mimeType.name = self.MIME_TYPE
        mimeType.description = "Embedded chaco widget"
        mimeType.fileExtensions = []
        plugin.mimeTypes = [mimeType]
        return [plugin]

    def create(self, mimeType, model_id, argNames, argValues):
        if mimeType != self.MIME_TYPE:
            return None

        # Put the args in a dictionary so it is easy to fetch the one(s) we
        # are interested in below. These names/values come from the
        # <object> tag attributes or the <param> tags inside the <object> tag.
        args = dict()
        for name, value in zip(argNames, argValues):
            args[name] = value
        plugin_widget = ChacoWidget(model_id=int(model_id.path()))
        return plugin_widget

class ChacoPlotEditor(BasicEditor):

    def html(self):
        template_str = dedent("""
                        <object type="application/x-chacowidget"
                                data=${obj_id}
                                width="400" height="300">
                        </object>
                       """)
        return Template(template_str).render(obj_id=id(self.obj))

    def setup_session(self, session=None):
        # Turn on allowing plugins
        global_settings = QtWebKit.QWebSettings.globalSettings()
        global_settings.setAttribute(QtWebKit.QWebSettings.PluginsEnabled, True)
        global_settings.setAttribute(QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)

        webview = session.widget.control
        page = webview.page()
        factory = ChacoWidgetFactory(webview)
        page.setPluginFactory(factory)
