from traits.api import Int, Str, Bool, Float, Enum, Range, List, Instance

from jigna.editors.api import IntEditor, FloatEditor, BoolEditor, \
    StringEditor, EnumEditor, RangeEditor, ListEditor, InstanceEditor, \
    ChacoPlotEditor

def get_editor(ttype, **kwargs):
    factory_mapping = {Int: {'simple': IntEditor},
                       Str: {'simple': StringEditor},
                       Float: {'simple': FloatEditor},
                       Range: {'simple': RangeEditor},
                       Bool: {'simple': BoolEditor},
                       Enum: {'simple': EnumEditor},
                       List: {'simple': ListEditor},
                       Instance: {'simple': InstanceEditor}}

    editor = factory_mapping.get(ttype.__class__)
    if editor:
        return editor.get(kwargs.get('style', 'simple'))
    else:
        raise ValueError('Unsupported trait type "%s"- no editor found!' %
                        ttype.__class__)

from traitsui.api import EditorFactory

class _TU_ChacoPlotEditor(EditorFactory):
    pass

class _TU_RangeEditor(EditorFactory):
    pass


tu_to_jigna_mapping = {_TU_ChacoPlotEditor: ChacoPlotEditor, 
                       _TU_RangeEditor: RangeEditor}
    