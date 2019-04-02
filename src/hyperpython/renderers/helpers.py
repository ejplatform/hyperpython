import re

from markupsafe import Markup
from sidekick import import_later

lxml_html = import_later("lxml.html")
lxml_etree = import_later("lxml.etree")
head_children = re.compile(r"^<(?:title|meta|script|style|link)")


def render_pretty(source, raw=False):
    """
    Pretty prints HTML source or element.

    Returns a Markup strings.
    """

    if not isinstance(source, str):
        source = source.render()

    root = lxml_html.fromstring(source)
    pretty = lxml_etree.tostring(root, encoding="unicode", pretty_print=True)

    # lxml adds <head> and <html> tags if the root tag should be
    if source.startswith("<head"):
        pretty = dedent(pretty[7:-8], 2)
    elif head_children.match(source):
        pretty = dedent(pretty[16:-18], 4)

    if raw:
        return pretty
    else:
        return Markup(pretty)


def dedent(st, size):
    return "\n".join(line[size:] for line in st.splitlines())
