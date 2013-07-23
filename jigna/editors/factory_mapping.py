from traits.api import Int, Str, Bool, Float, Enum, Range, List, Instance

from jigna.editors.api import IntEditor as JIntEditor, FloatEditor as JFloatEditor, \
    BoolEditor as JBoolEditor, StringEditor as JStringEditor, EnumEditor as JEnumEditor, \
    RangeEditor as JRangeEditor, ListEditor as JListEditor, InstanceEditor as JInstanceEditor

from traitsui.api import TextEditor, RangeEditor, EnumEditor, ListEditor, InstanceEditor, \
    BooleanEditor

class FactoryMapping(object):

    traitsui_to_jigna_editor = {
                          TextEditor: JStringEditor,
                          RangeEditor: JRangeEditor,
                          EnumEditor: JEnumEditor,
                          ListEditor: JListEditor,
                          InstanceEditor: JInstanceEditor,
                          BooleanEditor: JBoolEditor,
                        }

    trait_to_jigna_editor = {
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
    def get_editor_factory_for_ttype(cls, trait_type):
      """ Get the editor factory corresponding to the given trait type.
      """
      editor_factory_dict = cls.trait_to_jigna_editor.get(trait_type)
      if not editor_factory_dict:
          raise ValueError('Unsupported trait type "%s"- no editor found!' %
                          trait_type.__class__)
      else:
          return editor_factory_dict.get('simple')

    @classmethod
    def get_editor_factory(cls, obj, item):
        """ Get the Jigna editor factory for given traitsui `Item`
        """
        editor_factory = cls.traitsui_to_jigna_editor.get(item.editor.__class__)
        if not editor_factory:
            trait_type = obj.trait(item.name).trait_type.__class__
            editor_factory = cls.get_editor_factory_for_ttype(trait_type)
        return editor_factory

    @classmethod
    def register_traitsui_mapping(cls, traitsui_factory, jigna_factory):
        """ Register the mapping between the given traitsui editor factory and the
        corresponding Jigna editor factory.

        This means that a traitsui item edited with an editor of class `traitsui_factory`,
        it will be shown in HTML using an editor of class `jigna_factory`
        """
        cls.traitsui_to_jigna_editor[traitsui_factory] = jigna_factory

    @classmethod
    def register_trait_mapping(self, trait_type, jigna_factory, style='simple'):
        """ Register the mapping between the given traitsui editor factory and the
        corresponding Jigna editor factory.

        This means that a trait of type `trait_type` will be edited with `jigna_factory`
        unless another editor is specified explicitly.
        """
        jigna_factory_dict = cls.trait_to_jigna_editor.get(trait_type, None)
        if not jigna_factory_dict:
            jigna_factory_dict = {style: jigna_factory}
        else:
            jigna_factory_dict[style] = jigna_factory
        cls.trait_to_jigna_editor[trait_type] = jigna_factory_dict


def register_extra_traitsui_mappings():
    try:
        from mayavi.core.ui.api import SceneEditor
        from jigna.editors.api import MayaviPlotEditor
        FactoryMapping.register_traitsui_mapping(SceneEditor, MayaviPlotEditor)
    except ImportError:
        pass

    try:
        from enable.api import ComponentEditor
        from jigna.editors.api import ChacoPlotEditor
        FactoryMapping.register_traitsui_mapping(ComponentEditor, ChacoPlotEditor)
    except ImportError:
        pass

def register_extra_trait_mappings():
    pass

register_extra_traitsui_mappings()
register_extra_trait_mappings()
