from traits.api import Int, Str, Bool, Float, Enum, List, Instance

from jigna.editors.api import IntEditor, FloatEditor, BoolEditor, \
    StringEditor, EnumEditor, ListEditor, InstanceEditor

def get_editor(obj, tname, **kwargs):
    factory_mapping = {Int: {'simple': IntEditor},
                   Str: {'simple': StringEditor},
                   Float: {'simple': FloatEditor},
                   Bool: {'simple': BoolEditor},
                   Enum: {'simple': EnumEditor},
                   List: {'simple': ListEditor},
                   Instance: {'simple': InstanceEditor}}

    trait = obj.trait(tname)
    editor = factory_mapping.get(trait.trait_type.__class__)
    if editor:
        return editor.get('simple')(obj=obj, tname=tname, **kwargs)
    else:
        raise ValueError('Unsupported trait type "%s"- no editor found!' %
                        trait.trait_type.__class__)
