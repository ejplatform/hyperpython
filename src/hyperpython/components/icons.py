from .fa_icons import COLLECTIONS as FA_COLLECTIONS
from ..tags import i, a


def icon(icon, href=None, icon_class=lambda x: x, **kwargs):
    """
    Returns a icon tag.

    Args:
        icon (str):
            Name of the icon.
        href (str):
            If given, it wraps the results into a anchor link.
        icon_class (callable):
            A function that maps an icon name into the corresponding class or
            list of classes that should be added to the icon.
    """
    if href:
        return a(_icon(icon, **kwargs), href=href)
    return i(**kwargs).add_class(icon_class(icon))


def fa_icon(icon, href=None, collection=None, **kwargs):
    """
    Font awesome icon.

    Args:
        icon (str):
            Name of the icon.
        href (str):
            If given, it wraps the results into a anchor link.
        collection ('fa', 'fab', 'far', 'fal', 'fas'):
            The font-awesome collection:
                * fa/far/regular: regular icons
                * fab/brand: brand icons
                * fal/light: light icons
                * fas/solid: solid icons

    Examples:

        >>> fa_icon('face')
        <i class="fa fa-face"></i>
    """
    if collection is None:
        collection = FA_COLLECTIONS.get(icon, 'fa')
    if href:
        return a(fa_icon(icon, collection=collection, **kwargs), href=href)
    return _icon(icon, href, lambda x: [collection, f'fa-{icon}'], **kwargs)


_icon = icon
