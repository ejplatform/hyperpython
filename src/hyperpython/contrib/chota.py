import hyperpython as hp
from hyperpython import *  # noqa: F403

# TODO: this is a work in progress.
# See more: https://jenil.github.io/chota/
from hyperpython.core import Blob

CHOTA_CSS = hp.link(rel="stylesheet", href="//unpkg.com/chota@latest")
ROOT_CSS = """
:root {{
  --color-primary: {color_primary};
  --color-lightGrey: {color_light_grey};
  --color-grey: {color_grey};
  --color-darkGrey: {color_dark_grey};
  --color-error: {color_error};
  --color-success: {color_success};
  --grid-maxWidth: {grid_max_width};
  --grid-gutter: {grid_gutter};
  --font-size: {font_size};
  --font-family: {font_family};
}}
"""


def options(**kwargs):
    lines = [":root {"]
    properties = {
        "color_primary": "--color-primary",
        "color_light_grey": "--color-lightGrey",
        "color_grey": "--color-grey",
        "color_dark_grey": "--color-darkGrey",
        "color_error": "--color-error",
        "color_success": "--color-success",
        "grid_max_width": "--grid-maxWidth",
        "grid_gutter": "--grid-gutter",
        "font_size": "--font-size",
        "font_family": "--font-family",
    }
    for k, v in kwargs.items():
        lines.append(f"  {properties[k]}: {v}")

    return hp.style(Blob("\n".join(lines)))


def cdn(**kwargs):
    """
    Provides basic imports from a CDN for chota.css.
    """
    return hp.Block([CHOTA_CSS, options(**kwargs)])


#
# Forms and buttons
#
def button(
    text,
    *,
    href=None,
    submit=False,
    reset=False,
    form=False,
    outline=False,
    clear=False,
    primary=False,
    secondary=False,
    dark=False,
    error=False,
    success=False,
    **kwargs,
):
    """
    A styled button element.

    Args:
        text (str or HTML element):
            Text content of the button.
        href (str):
            Optional hyperlink target. If given, the button is create as an
            anchor tag.
        submit (bool):
            If True, renders element as an <input type='submit'> element.
        reset (bool):
            If True, renders element as an <input type='reset'> element.
        form (bool):
            If True, renders element as an <input type='button'> element.
        outline (bool):
            If True, paints only the outline.
        clear:
            If True, renders a plain-text button with no background color or
            outline.
        primary (bool):
            Render button with strong color emphasis.
        secondary (bool):
            Render button with intermediate color emphasis.
        dark (bool):
            Render button with dark colors.
        success (bool):
            Render button with a color that denotes success (usually green).
        error (bool):
            Render button with a color that denotes failure (usually red).

        ``button`` also accepts additional HTML attributes as keyword arguments.
    """

    options = {
        "clear": clear,
        "outline": outline,
        "primary": primary,
        "secondary": secondary,
        "dark": dark,
        "error": error,
        "success": success,
    }
    classes = ["button"]
    classes.extend(cls for cls, enable in options.items() if enable)
    if href:
        return hp.a(text, href=href, **kwargs).add_class(classes)
    elif submit or reset or form:
        if not isinstance(text, (str, int, float)):
            raise ValueError("submit inputs do not accept rich element children.")
        kind = "submit" if submit else "reset" if reset else "button"
        return hp.input_(value=text, type=kind, **kwargs).add_class(classes)
    else:
        return hp.button(text, **kwargs).add_class(classes)


def label(*args, inline=False, **kwargs):
    """
    A regular label, with an additional inline option that renders the <label>
    inline, if given.
    """
    elem = hp.label(*args, **kwargs)
    return elem.add_class("label-inline") if inline else label


#
# Grid system
#
def container(*children, **kwargs):
    """
    Container root of a grid-based layout. Children are passed as arguments.
    """
    return hp.div(class_="container", children=children, **kwargs)


def row(*children, **kwargs):
    """
    A row that contains several columns as children.
    """
    children = [(_col_break() if x is ... else x) for x in children]
    return hp.div(class_="row", children=children, **kwargs)


def column(*children, size=None, **kwargs):
    """
    A single column inside a 12-columns based flexible row.

    Args:
        size (optional, 1 to 12):
            Number of columns this cell spans. Each row has 12 columns, do the
            math. If not given, automatically fill the remaining space
            distributing equally between each column.

        ``column`` also accepts additional HTML attributes as keyword arguments.
    """
    if size is None:
        class_ = "col"
    else:
        class_ = f"col-{size}"
    return hp.div(children, **kwargs).add_class(class_)


_col_break = lambda: div(class_="is-full-width")
