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
    return a(globals()['icon'](icon), href=href, **kwargs)


def fa(icon, **kwargs):
    """
    Font awesome icon.
    """
    cls = kwargs.pop('class_', ())
    return i(class_=['fa', f'fa-{icon}', *cls], **kwargs)


def fab(icon, **kwargs):
    """
    Font awesome brands icon.
    """
    cls = kwargs.pop('class_', ())
    return i(class_=['fab', f'fab-{icon}', *cls], **kwargs)


def fa_link(href, icon, **kwargs):
    """
    A font awesome icon inside a link.
    """
    return a(fa(icon), href=href, **kwargs)


def fab_link(href, icon, **kwargs):
    """
    A font awesome brand icon inside a link.
    """
    return a(fab(icon), href=href, **kwargs)
