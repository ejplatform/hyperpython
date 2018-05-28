from markupsafe import Markup

from sidekick import import_later
from .html import render_html
from ..utils import STR_TYPES

lxml_html = import_later('lxml.html')
lxml_etree = import_later('lxml.etree')


def join_classes(*args):
    """
    Similar to js_class, but returns a list of class strings.
    """

    result = []
    for arg in args:
        if not arg:
            continue
        elif isinstance(arg, STR_TYPES):
            result.extend(arg.split())
        else:
            result.extend([x for x in arg if x])
    return result


def js_class(*args):
    """
    Converts a list of classes into a JS compatible class string ignoring
    empty/null entries.

    Examples:
        >>> js_class('foo', 'bar', '')
        'foo bar'
        >>> js_class('foo', ['bar', 'baz'])
        'foo bar baz'
    """
    return ' '.join(join_classes(*args))


def render_pretty(source):
    """
    Pretty prints HTML source or element.

    Returns a Markup strings.
    """

    if not isinstance(source, str):
        source = render_html(source)

    root = lxml_html.fromstring(source)
    pretty = lxml_etree.tostring(root, encoding='unicode', pretty_print=True)
    return Markup(pretty)
