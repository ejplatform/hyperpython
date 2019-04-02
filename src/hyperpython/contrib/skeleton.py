import hyperpython as hp

# noinspection PyUnresolvedReferences
from hyperpython import *

RALEWAY = hp.link(
    rel="stylesheet", href="//fonts.googleapis.com/css?family=Raleway:400,300,600"
)
NORMALIZE_CSS = hp.link(
    rel="stylesheet", href="//cdn.rawgit.com/necolas/normalize.css/master/normalize.css"
)
SKELETON_CSS = hp.link(
    rel="stylesheet",
    href="//cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
)
COLUMN_MAP = [
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
]


def cdn():
    """
    Provides basic imports from a CDN for skeleton.css.

    It adds Raleway font from Google Fonts, and Normalize.css and Miligram.css
    from Rawgit.
    """
    return hp.Block([RALEWAY, NORMALIZE_CSS, SKELETON_CSS])


#
# Forms and buttons
#
def button(
    text, *, href=None, submit=False, reset=False, form=False, primary=False, **kwargs
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
        primary (bool):
            If True, renders a plain-text button with no background color or
            outline.

        ``button`` also accepts additional HTML attributes as keyword arguments.
    """
    classes = ["button"]
    if primary:
        classes.append("button-primary")

    if href:
        return hp.a(text, href=href, **kwargs).add_class(classes)
    elif submit or reset or form:
        if not isinstance(text, (str, int, float)):
            raise ValueError("submit inputs do not accept rich element children.")
        kind = "submit" if submit else "reset" if reset else "button"
        return hp.input_(value=text, type=kind, **kwargs).add_class(classes)
    else:
        return hp.button(text, **kwargs).add_class(classes)


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
    return hp.div(class_="row", children=children, **kwargs)


def column(*children, size=12, offset=None, **kwargs):
    """
    A single column inside a 12-columns based flexible row.

    Args:
        size (1 to 12):
            Number of columns this cell spans. Each row has 12 columns, do the
            math.
        offset (int):
            Column offset in the 12-column system.

        ``column`` also accepts additional HTML attributes as keyword arguments.
    """
    classes = [COLUMN_MAP[size - 1], "columns"]
    if offset is not None:
        name = COLUMN_MAP[offset - 1]
        classes.append(f"offset-by-{name}")
    return hp.div(children, **kwargs).add_class(classes)


#
# Utilities
#
def full_width(elem):
    """
    Renders element with 'width: 100%'
    """
    return elem.add_class("u-full-width")


def full_max_width(elem):
    """
    Renders element with 'max-width: 100%'
    """
    return elem.add_class("u-max-full-width")


def floating(to, elem):
    """
    Floats element to left, right or clear floating.
    """
    if to == "left":
        return elem.add_class("u-pull-left")
    elif to == "right":
        return elem.add_class("u-pull-right")
    elif to == "clear":
        return elem.add_class("u-cf")
    elif to is None:
        return elem
    else:
        raise ValueError("Invalid float direction")
