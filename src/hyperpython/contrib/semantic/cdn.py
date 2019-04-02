import hyperpython as hp

prefix = "//cdnjs.cloudflare.com/ajax/libs/semantic-ui"
version = "2.4.1"
full_components = {
    "accordion",
    "checkbox",
    "dimmer",
    "dropdown",
    "embed",
    "form",
    "modal",
    "nag",
    "popup",
    "progress",
    "rating",
    "reset",
    "search",
    "segment",
    "shape",
    "sidebar",
    "site",
    "sticky",
    "tab",
    "transition",
    "video",
}
css_components = {
    "ad",
    "breadcrumb",
    "button",
    "card",
    "comment",
    "container",
    "divider",
    "feed",
    "flag",
    "grid",
    "header",
    "icon",
    "image",
    "input",
    "item",
    "label",
    "list",
    "loader",
    "menu",
    "message",
    "placeholder",
    "rail",
    "statistic",
    "step",
    "table",
}
js_components = {"api", "visibility"}
all_components = {*full_components, *css_components, *js_components}


def cdn(components=None, exclude=None):
    """
    Return the default imports from Cloudflare CDN.
    """
    return hp.Block(cdn_link("all"))


def cdn_link(which=None, prefix=prefix, version=version, minify=True):
    path = f"{which}.min" if minify else which
    if which == "all":
        src = f"{prefix}/{version}/semantic"
        return [
            hp.script(src=src + ".js"),
            hp.link(rel="stylesheet", href=src + ".css"),
        ]
    elif which in css_components:
        src = f"{prefix}/{version}/components/{path}.css"
        return [hp.link(rel="stylesheet", href=src)]
    elif which in js_components:
        src = f"{prefix}/{version}/components/{path}.js"
        return [hp.script(src=src)]
    elif which in full_components:
        src = f"{prefix}/{version}/components/{path}"
        return [
            hp.script(src=src + ".js"),
            hp.link(rel="stylesheet", href=src + ".css"),
        ]
    elif which == "theme-basic":
        return [
            cdn_font(prefix, version, "basic", "icons", ext)
            for ext in ["eot", "svg", "ttf", "woff"]
        ]
    elif which == "theme-default":
        return [
            *(
                cdn_font(prefix, version, "default", "brand-icons", ext)
                for ext in ["eot", "svg", "ttf", "woff", "woff2"]
            ),
            *(
                cdn_font(prefix, version, "default", "icons", ext)
                for ext in ["eot", "otf", "svg", "ttf", "woff", "woff2"]
            ),
            *(
                cdn_font(prefix, version, "default", "outline-icons", ext)
                for ext in ["eot", "svg", "ttf", "woff", "woff2"]
            )
            # ../themes/default/assets/images/flags.png ?
        ]

    elif which == "theme-github":
        return [
            cdn_font(prefix, version, "github", "octicons-local", "ttf"),
            *(
                cdn_font(prefix, version, "github", "octicons", ext)
                for ext in ["svg", "ttf", "woff"]
            ),
        ]
    elif which == "theme-material":
        return [
            cdn_font(prefix, version, "material", "icons", ext)
            for ext in ["eot", "svg", "ttf", "woff", "woff2"]
        ]
    else:
        raise ValueError(f"invalid asset: {which}")


def cdn_font(prefix, version, theme, which, ext):
    src = f"{prefix}/{version}/themes/{theme}/assets/fonts/{which}.{ext}"
    return hp.font(src=src)
