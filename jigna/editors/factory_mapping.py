from traits.api import Int, Str, Bool, Float, Enum, Range, List, Instance

from jigna.editors.api import IntEditor as JIntEditor, FloatEditor as JFloatEditor, \
    BoolEditor as JBoolEditor, StringEditor as JStringEditor, EnumEditor as JEnumEditor, \
    RangeEditor as JRangeEditor, ListEditor as JListEditor, InstanceEditor as JInstanceEditor

from traitsui.api import TextEditor, RangeEditor, EnumEditor, ListEditor, InstanceEditor, \
    BooleanEditor

class FactoryMapping(object):

    traitsui_to_jigna_mapping = {
                                  TextEditor: JStringEditor, 
                                  RangeEditor: JRangeEditor,
                                  EnumEditor: JEnumEditor,
                                  ListEditor: JListEditor,
                                  InstanceEditor: JInstanceEditor,
                                  BooleanEditor: JBoolEditor,
                                }

    trait_type_to_editor_factory_mapping = {
                                         Int: {'simple': JIntEditor},
                                         Str: {'simple': JStringEditor},
                                         Float: {'simple': JFloatEditor},
                                         Range: {'simple': JRangeEditor},
                                         Bool: {'simple': JBoolEditor},
                                         Enum: {'simple': JEnumEditor},
                                         List: {'simple': JListEditor},
                                         Instance: {'simple': JInstanceEditor}
                                      }

    @classmethod
    def get_editor_factory(cls, obj, item):
        """ Get the Jigna editor factory for the given traitsui `Item` object.
        """
        editor_factory = cls.traitsui_to_jigna_mapping.get(item.editor.__class__)
        if not editor_factory:
            trait_type = obj.trait(item.name).trait_type.__class__
            editor_factory_dict = cls.trait_type_to_editor_factory_mapping.get(trait_type)
            if editor_factory_dict:
                return editor_factory_dict.get(item.style or 'simple')
            else:
                raise ValueError('Unsupported trait type "%s"- no editor found!' %
                                trait_type.__class__)
        return editor_factory

    @classmethod
    def register_editor_factory(cls, traitsui_factory, jigna_factory):
        """ Register the mapping between the given traitsui editor factory and the 
        corresponding Jigna editor factory. 

        This means that a traitsui item edited with an editor of class `traitsui_factory`, 
        it will be shown in HTML using an editor of class `jigna_factory`
        """
        cls.traitsui_to_jigna_mapping[traitsui_factory] = jigna_factory

def register_additional_factories():
    try:
        from mayavi.core.ui.api import SceneEditor
        from jigna.editors.api import MayaviPlotEditor
        FactoryMapping.register_editor_factory(SceneEditor, MayaviPlotEditor)
    except ImportError:
        pass

    try:
        from enable.api import ComponentEditor
        from jigna.editors.api import ChacoPlotEditor
        FactoryMapping.register_editor_factory(ComponentEditor, ChacoPlotEditor)
    except ImportError:
        pass

register_additional_factories()
