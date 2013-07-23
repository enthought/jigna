# Standard library imports
from mako.template import Template
from textwrap import dedent

# Enthought library imports
from traits.api import HasTraits

# Local imports
from jigna.editors.basic_editors import BasicEditor


class ListEditor(BasicEditor):

    def __init__(self, **traits):
        super(self.__class__, self).__init__(**traits)
        item_trait = self.obj.trait(self.tname).handler.item_trait
        item_trait_type = item_trait.trait_type.__class__

        from jigna.editors.factory_mapping import FactoryMapping
        self.editor_factory = FactoryMapping.get_editor_factory_for_ttype(item_trait_type)
        self.editors = []
        for i, item in enumerate(getattr(self.obj, self.tname)):
            editor = self.editor_factory(obj=self.obj,
                                         tname="%s[%s]"%(self.tname, i),
                                         label=str(i))
            self.editors.append(editor)

    def html(self):
        template_str = dedent("""
                         <div>
                          % for i, item in enumerate(items):
                              ${editors[i].html()}
                          % endfor
                         </div>
                       """)
        return Template(template_str).render(items=getattr(self.obj, self.tname),
                                             editors=self.editors)

    def js(self):
        template_str = dedent("""
                         % for i, item in enumerate(items):
                             ${editors[i].js()}
                         % endfor
                       """)
        return Template(template_str).render(items=getattr(self.obj, self.tname),
                                             editors=self.editors,
                                             tname=self.tname)

    def setup_session(self, session):
        def list_handler(obj, name, new_value):
            """ A handler specific to list trait type.
            """
            try:
                session._setting_trait = True
                traitchange_js = session._get_trait_change_js(self.obj, self.tname)
                session.widget.execute_js(traitchange_js)
            finally:
                session._setting_trait = False

        self.obj.on_trait_change(list_handler, self.tname+'[]')
