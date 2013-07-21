# Enthought library imports
from traitsui.api import View, Item

from traitsui_editor import TraitsUIWidget, TraitsUIEditor

###############################################################################
# MayaviPlotEditor class.
###############################################################################
class MayaviPlotEditor(TraitsUIEditor):

    def create_widget(self, model_id, args):
        width, height = self.get_size(args)
        from mayavi.core.ui.api import MayaviScene, SceneEditor
        view = View(Item(self.tname, show_label=False,
                         editor=SceneEditor(scene_class=MayaviScene)),
                         width=width, height=height, resizable=True)
        widget = TraitsUIWidget(self.obj, self.tname, view=view)
        return getattr(self.obj, self.tname).scene_editor.control
