import collections

from ..core import Element
from ..tags import a, p, span, h
from ..utils import escape, lazy_singledispatch


def a_or_p(*args, href=None, **kwargs):
    """
    Return a or p tag depending if href is defined or not.
    """

    if href:
        return a(*args, href=href, **kwargs)
    else:
        return p(*args, href=href, **kwargs)


def a_or_span(*args, href=None, **kwargs):
    """
    Return a or span tag depending if href is defined or not.
    """

    if href:
        return a(*args, href=href, **kwargs)
    else:
        return span(*args, **kwargs)


@lazy_singledispatch
def hyperlink(obj, href='#', **attrs) -> Element:
    """
    Converts object to an anchor (<a>) tags.

    It implements some common use cases:
        str:
            Renders string as content inside the <a>...</a> tags. Additional
            options including href can be passed as keyword arguments. If no
            href is given, it tries to parse a string of "Value <link>" and
            uses href='#' if no link is found.

        dict or mapping:
            Most keys are interpreted as attributes. The visible content of
            the link must be stored in the 'content' key:

            >>> hyperlink({'href': 'www.python.com', 'content': 'Python'})
            <a href="www.python.com">Python</a>

        django model:
            It must define a get_absolute_url() method. This function uses
            this result as the href field and str(model) as its content.

            >>> hyperlink(User(first_name='Joe', username='joe123'))
            <a href="/users/joe123">Joe</a>


    In order to support other types, use the lazy_singledispatch mechanism::

        @hyperlink.registerPlugin(MyFancyType)
        def _(x, **kwargs):
            return safe(render_object_as_safe_html(x))


    See Also:

        :func:`pyml.helpers.attrs`: See this function for an exact explanation
            of how keyword arguments are translated into HTML attributes.
    """

    try:
        render = obj.__html__
    except AttributeError:
        raise TypeError('type not supported: %s' % obj.__class__.__name__)
    else:
        data = render()
        attrs['href'] = href
        return h('a', attrs, [data])


@hyperlink.register(str)
def _hyperlink_str(data, href=None, **attrs):
    if href is None:
        data, href = parse_link(data)
    attrs['href'] = href
    return h('a', attrs, escape(data))


@hyperlink.register(collections.Mapping)
def _hyperlink_map(obj, **attrs):
    content = obj['content']
    for k, v in obj.items():
        if k != 'content':
            attrs.setdefault(k, v)
    return h('a', attrs, content)


@hyperlink.register('django.db.models.Model')
def _hyperlink_model(x, **attrs):
    href = attrs.get('href') or x.get_absolute_url()
    attrs.setdefault('href', href)
    return h('a', attrs, escape(str(x)))


def parse_link(name):
    """
    Return a tuple with (name, link) from a string of "name<link>".

    If no link is found, the second value is None.
    """
    if name.endswith('>'):
        name, sep, link = name.partition('<')
        if sep:
            return name.rstrip(), link[:-1]
    return name, None


def breadcrumbs(x, *paths, level=0, **kwargs):
    """
    Component thta Receives a list of links and return a breadcrumbs element.
    """
    raise NotImplementedError
