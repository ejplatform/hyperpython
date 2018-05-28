import collections
import io
from json import dumps as json_dumps

from ..utils import lazy_singledispatch


@lazy_singledispatch
def dump_single_attr(x, file):
    """
    Renders object as an HTML attribute value.

    It define the following dispatch rules:

    str:
        Quotations and & are escaped, any other content, including <, >, is
        allowed.
    numeric types:
        Are simply converted to strings.
    lists and mappings:
        Are converted to JSON and returned as safe strings. This is used in
        some modern javascript frameworks reads JSON from tag attributes.
    """
    raise TypeError('%s objects are not supported' % x.__class__.__name__)


def render_single_attr(x):
    """
    Like dump_single_attr(), but return a string instead of writing to a file.
    """
    file = io.StringIO()
    dump_single_attr(x, file)
    return file.getvalue()


@dump_single_attr.register(str)
def _(x, file):
    data = x.replace('&', '&amp;').replace('"', '&quot;')
    file.write(data)


# Register numeric types and all trivial conversions
for _tt in [int, float, complex, 'decimal.Decimal']:
    dump_single_attr.register(_tt, lambda x, file: file.write(str(x)))


# JSON conversions
@dump_single_attr.register(collections.Sequence)
@dump_single_attr.register(collections.Mapping)
def _(x, file):
    dump_single_attr(json_dumps(x), file)
