from jigna.editor_factories import get_editor


class View(object):
    def __init__(self, group, **kwargs):
        self.content = group

    def render(self, model):
        child = self.content
        return '<div class="container">' + child.render(model) + '</div>'


class Group(object):
    def __init__(self, *items, **kwargs):
        self.content = items
        self.orientation = kwargs.pop('orientation', 'vertical')

    def render(self, model):
        ret_val = '<div class="row">'
        TOTAL_COLUMNS = 12

        if self.orientation == 'horizontal':
            n_columns = TOTAL_COLUMNS // len(self.content)
            item_class = "span%s" % n_columns
            for content in self.content:
                ## XXX: ideally this should be added to the editor
                ret_val += '<div class="%s">' % item_class
                ret_val += content.render(model)
                ret_val += '</div>'
        else:
            # default orientation is vertical
            for content in self.content:
                ## XXX: ideally this should be added to the editor
                ret_val += '<div>'
                ret_val += content.render(model)
                ret_val += '</div>'
        ret_val += '</div>'
        return ret_val


class Item(object):
    def __init__(self, name):
        self.name = name

    def render(self, model):
        return get_editor(model, self.name).html()
