from ..tags import i, a


def icon(icon, **kwargs):
    """
    Returns a icon tag.
    """
    cls = kwargs.pop('class_', ())
    return i(class_=[*icon.split(), *cls], **kwargs)


def icon_link(href, icon, **kwargs):
    """
    Returns an icon tag inside a anchor element.
    """
    return a(_icon(icon), href=href, **kwargs)


def fa_icon(icon, **kwargs):
    """
    Font awesome icon.
    """
    cls = kwargs.pop('class_', ())
    return i(class_=['fa', f'fa-{icon}', *cls], **kwargs)


def fab_icon(icon, **kwargs):
    """
    Font awesome brands icon.
    """
    cls = kwargs.pop('class_', ())
    return i(class_=['fab', f'fa-{icon}', *cls], **kwargs)


def fa_link(href, icon, **kwargs):
    """
    A font awesome icon inside a link.
    """
    return a(fa_icon(icon), href=href, **kwargs)


def fab_link(href, icon, **kwargs):
    """
    A font awesome brand icon inside a link.
    """
    return a(fab_icon(icon), href=href, **kwargs)


_icon = icon
