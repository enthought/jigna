from traits.api import Int, Str, Bool, Float, Enum

from jigna.editors.api import IntEditor, FloatEditor, BoolEditor, \
    StringEditor, EnumEditor
    
factory_mapping = {Int: {'simple': IntEditor},
                   Str: {'simple': StringEditor},
                   Float: {'simple': FloatEditor},
                   Bool: {'simple': BoolEditor},
                   Enum: {'simple': EnumEditor}}
    
def get_editor(obj, tname):
    trait = obj.trait(tname)
    editor = factory_mapping.get(trait.trait_type.__class__)
    if editor:
        return editor.get('simple')(obj=obj, tname=tname)
    else:
        raise ValueError('Unsupported trait type - no editor found!')