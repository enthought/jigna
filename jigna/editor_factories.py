from traits.api import Int, Str, Bool, Float, Enum, List, Instance

from jigna.editors.api import IntEditor, FloatEditor, BoolEditor, \
    StringEditor, EnumEditor, ListEditor, InstanceEditor

def get_editor(ttype, **kwargs):
    factory_mapping = {Int: {'simple': IntEditor},
                       Str: {'simple': StringEditor},
                       Float: {'simple': FloatEditor},
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
