from traitsui.api import View, Group, Item


def _get_trait_view(model):
    view = model.trait_view()
    return view


def _render(obj):
    if isinstance(obj, View):
        return _render_view(obj)
    elif isinstance(obj, Group):
        return _render_group(obj)
    elif isinstance(obj, Item):
        return _render_item(obj)
    else:
        raise Exception('Object %s of unknown type %s found' %
            (obj, obj.__class__))


def _render_view(view):
    child = view.content
    ## Is a View's child always a Group ?
    return _render(child)


def _render_group(group):
    ret_val = '<div class="container">'
    for content in group.content:
        ret_val += _render(content)
    ret_val += '</div>'
    return ret_val


def _render_item(item):
    ret_val = "%s <br/>" % (item.name)
    return ret_val


def render(session):
    '''
    :param obj: is a `jigna.session.Session` object
    '''
    html_views = session.views
    html = ''
    for view in html_views:
        trait_view = view.model.trait_view()
        html += _render_view(trait_view)
    return html
