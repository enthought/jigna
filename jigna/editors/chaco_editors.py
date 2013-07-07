from textwrap import dedent
from mako.template import Template

# Enthought library imports
from traitsui.api import View, Item
from enable.component_editor import ComponentEditor

from jigna.editors.basic_editors import BasicEditor
from traitsui_widget_factory import TraitsUIWidgetFactory, TraitsUIWidget

###############################################################################
# ChacoPlotEditor class.
###############################################################################
class ChacoPlotEditor(BasicEditor):

    def html(self):
        template_str = dedent("""
                        <object type="application/x-traitsuiwidget"
                                data=${obj_id} trait_name="${trait_name}"
                                width="400" height="400">
                        </object>
                       """)
        return Template(template_str).render(obj_id=id(self.obj),
                                             trait_name=self.tname)

    def setup_session(self, session=None):
        webview = session.widget.control
        TraitsUIWidgetFactory.setup_session(webview)
        my_id = id(self.obj)
        TraitsUIWidgetFactory.register_factory(my_id, self.tname,
                                               self.create_widget)

    def create_widget(self, model_id, args):
        width = int(args.get('width', 400))
        height = int(args.get('height', 400))
        view = View(Item(self.tname, style='custom', show_label=False,
                         editor=ComponentEditor()),
                         width=width, height=height, resizable=True)
        plugin_widget = TraitsUIWidget(self.obj, self.tname, view=view)
        return plugin_widget
