from .fa_icons import COLLECTIONS as FA_COLLECTIONS
from ..tags import i, a


def icon(name, href=None, icon_class=lambda x: x, icon_data=lambda x: [], **kwargs):
    """
    Returns a icon tag.

    Args:
        name (str):
            Name of the icon.
        href (str):
            If given, it wraps the results into a anchor link.
        icon_class (callable):
            A function that maps an icon name into the corresponding class or
            list of classes that should be added to the icon.
    """
    if href:
        return a(
            icon(name, icon_class=icon_class, icon_data=icon_data, **kwargs), href=href
        )
    return i(children=icon_data(name), **kwargs).add_class(icon_class(name), first=True)


def fa_icon(name, href=None, collection=None, **kwargs):
    """
    Font awesome icon.

    Args:
        name (str):
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

        >>> print(fa_icon('face'))
        <i class="fa fa-face"></i>
    """
    if collection is None:
        collection = FA_COLLECTIONS.get(name, "fa")
    if href:
        return a(fa_icon(name, collection=collection, **kwargs), href=href)
    return icon(name, href, lambda x: [collection, f"fa-{name}"], **kwargs)
