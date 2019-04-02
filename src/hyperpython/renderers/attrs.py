import collections.abc
import io

from sidekick import lazy_singledispatch

from .single_attr import dump_single_attr
from ..utils import html_natural_attr


@lazy_singledispatch
def dump_attrs(obj, file):
    """
    Convert object into a list of key-value HTML attributes.

    Args:
        obj:
            Object representing a sequence of arguments.
        file:
            A file-like descriptor.


    Observations:
        This function uses multiple dispatch, so the behaviour might differ a
        little bit depending o the first argument.

        mappings:
            Renders key-values into the corresponding HTML results.
        sequences:
            Any non-string sequence is treated as sequence of (key, value)
            pairs. If any repeated keys are found, it keeps only the last value.
        *attrs* protocol:
            Any object that define an ``attrs`` attribute that can be either a
            mapping or a sequence of pairs.

        In all cases, ``attrs`` takes arbitrary keyword attributes that are
        interpreted as additional attributes. PyML converts all underscores
        present in the attribute names to dashes since this is the most common
        convention in HTML.
    """
    data = getattr(obj, "attrs", None)
    if data is not None and type(data) is not type(obj):
        return dump_attrs(data, file)
    raise TypeError("%s objects are not supported" % obj.__class__.__name__)


def render_attrs(obj, **kwargs):
    """
    Like dump_attrs, but return a string instead of writing to a file.
    """
    file = io.StringIO()
    dump_attrs(obj, file)
    idx = file.tell()
    if kwargs:
        if idx:
            file.write(" ")
        kwargs = {html_natural_attr(k): v for k, v in kwargs.items()}
        dump_attrs(kwargs, file)
    return file.getvalue().rstrip()


@dump_attrs.register(type(None))
def _attrs_none(_, file):
    _attrs_mapping({}, file)


@dump_attrs.register(collections.abc.Mapping)
def _attrs_mapping(dic, file):
    _attrs_sequence(dic.items(), file)


@dump_attrs.register(bytes)
@dump_attrs.register(str)
def _attrs_str(*_args):
    raise TypeError("strings types are not supported")


@dump_attrs.register(collections.abc.Sequence)  # noqa: C901
def _attrs_sequence(seq, file):
    write = file.write
    elements = 0

    for attr, value in seq:
        if value is False or value is None:
            continue
        elif value is True:
            write(attr)
            write(" ")
        elif attr == "class":
            if value:
                write('class="')
                if isinstance(value, str):
                    write(value)
                elif isinstance(value, dict):
                    write(" ".join(str(v) for k, v in value.items() if v))
                else:
                    write(" ".join(value))
                write('" ')
            else:
                continue
        else:
            write(attr)
            write('="')
            dump_single_attr(value, file)
            write('" ')
        elements += 1

    if elements:
        file.seek(file.tell() - 1)
