# Enthought library imports
from traitsui.api import View, Item
from enable.api import ComponentEditor

from traitsui_editor import TraitsUIWidget, TraitsUIEditor

###############################################################################
# ChacoPlotEditor class.
###############################################################################
class ChacoPlotEditor(TraitsUIEditor):

    def create_widget(self, model_id, args):
        width, height = self.get_size(args)
        view = View(Item(self.tname, style='custom', show_label=False,
                         editor=ComponentEditor()),
                         width=width, height=height, resizable=True)
        plugin_widget = TraitsUIWidget(self.obj, self.tname, view=view)
        return plugin_widget
