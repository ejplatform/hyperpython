import sidekick as sk

from ..core import Element, Component
from ..tags import span, div
from ..utils import safe

ELEM = (Element, Component)

_markdown = sk.import_later("markdown:markdown")


def markdown(text, *, output_format="html5", **kwargs):
    """
    Renders Markdown content as HTML and return as a safe string.

    >>> print(markdown('# Hello!'))
    <h1>Hello!</h1>
    """
    return safe(_markdown(text, output_format=output_format, **kwargs))


def elem_or_span(elem):
    """
    Return tags arguments, but wrap text in spans.

    >>> print(elem_or_span('hello'))
    <span>hello</span>
    """
    return elem_or_wrap(elem, span)


def elem_or_div(elem):
    """
    Return tags arguments, but wrap text in divs.
    """
    return elem_or_wrap(elem, div)


def elem_or_wrap(elem, tag):
    """
    Return tags arguments, but wrap text in with the given tag.
    """
    return elem if isinstance(elem, ELEM) else tag(elem)
