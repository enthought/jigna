# Standard library imports
from textwrap import dedent
from mako.template import Template

# Enthought library imports
from traitsui.api import View, Item, Group

# Local imports
from jigna.editor_factories import get_editor, tu_to_jigna_mapping

class JView(object):

    def __init__(self, tu_view, model):
        """ Constructor for the JView object.

        tu_view : A traitsui `View` object
        """
        self.tu_view = tu_view
        self.model = model
        self.items = tu_view.content.content

    def render(self):
        template_str = dedent(""" 
            <div class="container">
                % for item in items:
                    <div class="row">
                        ${render_layout(item, model)}
                    </div>
                % endfor
            </div>
            """)
        return Template(template_str).render(items=self.items, model=self.model, 
                                             render_layout=render_layout)

class JGroup(object):

    def __init__(self, tu_group, model):
        """ Constructor for the JView object.

        tu_group : A traitsui `Group` object
        """
        self.tu_group = tu_group
        self.model = model
        self.items = tu_group.content

    def render(self):
        template_str = dedent(""" 
            <%
                TOTAL_COLUMNS = 12
                n_columns = TOTAL_COLUMNS // len(items)
            %>
            % if orientation == "horizontal":
                % for item in items:
                    <div class="span${n_columns}">
                        ${render_layout(item, model)}
                    </div>
                % endfor
            % elif orientation == "vertical":
                <div class="span12">
                    % for item in items:
                        ${render_layout(item, model)}
                    % endfor
                </div>
            % endif
            """)
        return Template(template_str).render(items=self.items, model=self.model,
                                             render_layout=render_layout, 
                                             orientation=self.tu_group.orientation)

class JItem(object):

    def __init__(self, tu_item, model):
        """ Constructor for the JView object.

        tu_item : A traitsui `Item` object
        """
        self.tu_item = tu_item
        self.model = model
        if getattr(self.tu_item, 'editor'):
            editor_factory = tu_to_jigna_mapping[self.tu_item.editor.__class__]
            editor_args = getattr(self.tu_item, 'editor_args')
        else:
            ttype = self.model.trait(self.tu_item.name).trait_type
            editor_factory = get_editor(ttype)
            editor_args = getattr(self.tu_item, 'editor_args')
        self.editor = editor_factory(obj=self.model, 
                                     tname=self.tu_item.name, 
                                     **editor_args)

    def render(self):
        return self.editor.html()

def render_layout(layout, model):    
    if isinstance(layout, View):
        return JView(layout, model).render()
    elif isinstance(layout, Group):
        return JGroup(layout, model).render()
    elif isinstance(layout, Item):
        return JItem(layout, model).render()

def get_items(layout):
    """ Return a list of `Item` objects in a given layout
    """
    items = []
    if isinstance(layout, View):
        for item in layout.content.content:
            items += get_items(item)
    if isinstance(layout, Group):
        for item in layout.content:
            items += get_items(item)
    if isinstance(layout, Item):
        items += [layout]
    return items