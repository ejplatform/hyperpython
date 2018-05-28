import sidekick as sk
from hyperpython.utils import safe

_markdown = sk.import_later('markdown:markdown')


def markdown(text, *, output_format='html5', **kwargs):
    """
    Renders Markdown content as HTML and return as a safe string.
    """
    return safe(_markdown(text, output_format=output_format, **kwargs))
