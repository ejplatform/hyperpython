from .fa_icons import COLLECTIONS as FA_COLLECTIONS
from ..tags import i, a


def icon(icon, href=None, icon_class=lambda x: x, **kwargs):
    """
    Returns a icon tag.

    If an href attribute is passed, it wraps the results into a anchor link.
    """
    if href:
        return a(_icon(icon, href=href, **kwargs))
    return i(**kwargs).add_class(icon_class(icon))


def fa_icon(icon, href=None, collection=None, **kwargs):
    """
    Font awesome icon.
    """
    if collection is None:
        collection = FA_COLLECTIONS.get(icon, 'fa')
    return _icon(icon, href, lambda x: [collection, f'fa-{icon}'], **kwargs)


def fab_icon(icon, href=None, **kwargs):
    """
    Font awesome brands icon.
    """
    return fab_icon(icon, href, collection='fab', **kwargs)


_icon = icon
