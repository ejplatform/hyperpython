import collections.abc
import io
from json import dumps as json_dumps

from markupsafe import Markup

from sidekick import lazy_singledispatch


# noinspection PyUnusedLocal
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
    raise TypeError("%s objects are not supported" % x.__class__.__name__)


def render_single_attr(x):
    """
    Like dump_single_attr(), but return a string instead of writing to a file.
    """
    file = io.StringIO()
    dump_single_attr(x, file)
    return file.getvalue()


@dump_single_attr.register(str)
def _single_attr_str(x, file):
    data = x.replace("&", "&amp;").replace('"', "&quot;")
    file.write(data)


@dump_single_attr.register(Markup)
def _single_attr_str(x, file):
    file.write(x)


# Register numeric types and all trivial conversions
for _tt in [int, float, complex, "decimal.Decimal"]:
    dump_single_attr.register(_tt, lambda x, file: file.write(str(x)))


# JSON conversions
@dump_single_attr.register(collections.abc.Sequence)
@dump_single_attr.register(collections.abc.Mapping)
def _single_attr_json_data(x, file):
    dump_single_attr(json_dumps(x), file)
