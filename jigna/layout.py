from jigna.editor_factories import get_editor
from traitsui.api import View, Group, Item


def _get_trait_view(model):
    view = model.trait_view()
    return view


def _render(obj, model):
    if isinstance(obj, View):
        return _render_view(obj, model)
    elif isinstance(obj, Group):
        return _render_group(obj, model)
    elif isinstance(obj, Item):
        return _render_item(obj, model)
    else:
        raise Exception('Object %s of unknown type %s found' %
            (obj, obj.__class__))


def _render_view(view, model):
    child = view.content
    ## Is a View's child always a Group ?
    return '<div class="container">' + _render(child, model) + '</div>'


def _render_group(group, model):
    ret_val = '<div class="row">'
    for content in group.content:
        ret_val += _render(content, model)
    ret_val += '</div>'
    return ret_val


def _render_item(item, model):
    # from IPython.core.debugger import Tracer; Tracer()()
    ret_val = get_editor(model, item.name).html()
    return ret_val


def render(session):
    '''
    :param obj: is a `jigna.session.Session` object
    '''
    html_views = session.views
    html = ''
    for view in html_views:
        trait_view = view.model.trait_view()
        html += _render(trait_view, view.model)
    return html
