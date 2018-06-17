from markupsafe import Markup

from sidekick import import_later
from .html import render_html

lxml_html = import_later('lxml.html')
lxml_etree = import_later('lxml.etree')


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
