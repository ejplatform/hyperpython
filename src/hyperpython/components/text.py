import sidekick as sk

from hyperpython import span, div
from ..utils import safe

_markdown = sk.import_later('markdown:markdown')


def markdown(text, *, output_format='html5', **kwargs):
    """
    Renders Markdown content as HTML and return as a safe string.
    """
    return safe(_markdown(text, output_format=output_format, **kwargs))


def elem_or_span(elem):
    if isinstance(elem, str):
        return span(elem)
    else:
        return elem


def elem_or_div(elem):
    if isinstance(elem, str):
        return div(elem)
    else:
        return elem
