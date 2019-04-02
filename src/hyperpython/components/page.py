from types import MappingProxyType

from ..core import Block, Component
from ..tags import link, meta, script, title, head

APPLE_TOUCH_ICONS = {"57x57", "72x72", "114x114", 57, 72, 114}


def stylesheets(sheets):
    """
    Render a list of stylesheets paths as a series of <link> tags.
    """
    return Block([link(rel="stylesheet", href=sheet) for sheet in sheets])


def scripts(urls, **kwargs):
    """
    Receives a list of urls and return a series of <script> tags.

    Any extra arguments (e.g., defer=True) are passed as arguments to the
    <script> tags.
    """
    return Block([script(src=url, **kwargs) for url in urls])


def meta_values(data, **kwargs):
    """
    Receives a mapping of {header: value} pairs and return a series of
    <meta http-equiv={header} content={value}> tags.
    """
    data = join_dicts(data, kwargs)
    return Block([meta(http_equiv=k, content=v) for k, v in data.items()])


def meta_headers(data, **kwargs):
    """
    Receives a mapping of {name: value} pairs and return a series of
    <meta name={name} content={value}> tags.
    """
    data = join_dicts(data, kwargs)
    return Block([meta(name=k, content=v) for k, v in data.items()])


def meta_properties(data, **kwargs):
    """
    Receives a mapping of {name: value} pairs and return a series of
    <meta property={name} content={value}> tags.
    """
    data = join_dicts(data, kwargs)
    return Block([meta(property=k, content=v) for k, v in data.items()])


def meta_og(data, **kwargs):
    """
    Receives a mapping of {name: value} pairs and return a series of
    <meta property="og:{name}" content={value}> tags.

    Those tags are used by the Open Graph protocol (http://ogp.me/) to index
    information for search engines and social networks such as Facebook.
    """
    data = join_dicts(data, kwargs)
    return meta_properties({"og:" + k: v for k, v in data.items()})


def favicons(data):
    """
    Receives a mapping of {size: url} pairs and return a series of
    <link rel="icon" size={size} href={url}> tags.

    It automatically recognizes resolutions 57x57, 72x72, 114x114 as being of
    type apple-touch-icon.
    """

    icons = []
    for size, url in data.items():
        if size is None or size == "default":
            icons.append(link(rel="icon", href=url))
        elif size in APPLE_TOUCH_ICONS:
            size = as_icon_size(size)
            icons.append(link(rel="apple-touch-icon", size=size, href=url))
        else:
            size = as_icon_size(size)
            icons.append(link(rel="icon", size=size, href=url))

    return Block(icons)


def google_analytics(property_id, defer=False):
    """
    Return a Google analytics script tag.
    """
    return script(
        """
(function(i, s, o, g, r, a, m) {
i['GoogleAnalyticsObject'] = r;
i[r] = i[r] | | function ()
{
    (i[r].q = i[r].q | |[]).push(arguments)
}, i[r].l = 1 * new
Date();
a = s.createElement(o), m = s.getElementsByTagName(o)[0];
a.async = 1;
a.src = g;
m.parentNode.insertBefore(a, m)
})(window, document, 'script', 'https://www.google-analytics.com/analytics.js', 'ga');
ga('create', '%s', 'auto');"""
        % property_id,
        defer=defer,
    )


class Head(Component):
    """
    Stores all information typically found on the <head> section of a web page.
    """

    google_analytics_id = None
    stylesheets = ()
    scripts = ()
    icons = MappingProxyType({})
    favicons = MappingProxyType({})
    meta_values = MappingProxyType({})
    meta_headers = MappingProxyType({})
    meta_properties = MappingProxyType({})

    # noinspection PyShadowingNames
    def __init__(
        self,
        title,
        charset="utf8",
        viewport="width=device-width, initial-scale=1",
        og_type="website",
        **kwargs,
    ):
        self.title = title
        self.charset = charset
        self.viewport = viewport
        self.og_type = og_type

        for k, v in kwargs.items():
            setattr(self, k, v)

    def html(self):
        return head(
            [
                meta(charset=self.charset),
                title(self.title),
                meta(name="viewport", content=self.viewport),
                *self.meta_values_tags(),
                *self.meta_headers_tags(),
                *self.meta_properties_tags(),
                *self.open_graph_tags(),
                *self.css_tags(),
                *self.script_tags(),
                *self.google_analytics_tag(),
                *self.favicon_tags(),
            ]
        )

    def open_graph_tags(self):
        data = {
            "title": getattr(self, "og_title", self.title),
            "type": getattr(self, "og_type", "website"),
        }
        clean_data = {k: v for k, v in data.items() if v is not None}
        return meta_og(clean_data).children

    def meta_values_tags(self):
        return meta_values(self.meta_values).children

    def meta_headers_tags(self):
        return meta_headers(self.meta_headers).children

    def meta_properties_tags(self):
        return meta_properties(self.meta_properties).children

    def google_analytics_tag(self):
        if self.google_analytics_id:
            return google_analytics(self.google_analytics_id).children
        else:
            return []

    def css_tags(self):
        return stylesheets(self.stylesheets or ()).children

    def script_tags(self):
        return scripts(self.scripts or ()).children

    def favicon_tags(self):
        return favicons(self.favicons).children


#
#  Auxiliary functions
#
def join_dicts(data, kwargs):
    if kwargs:
        kwargs = {k.replace("_", "-"): v for k, v in kwargs.items()}
        return dict(data, **kwargs)
    return data


def as_icon_size(value):
    if isinstance(value, int):
        return f"{value}x{value}"
    return value
