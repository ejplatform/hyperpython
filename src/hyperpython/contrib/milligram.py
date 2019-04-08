import hyperpython as hp
from hyperpython import *

ROBOTO = hp.link(
    rel="stylesheet",
    href="//fonts.googleapis.com/css?family=Roboto:300,300italic,700,700italic",
)
NORMALIZE_CSS = hp.link(
    rel="stylesheet", href="//cdn.rawgit.com/necolas/normalize.css/master/normalize.css"
)
MILIGRAM_CSS = hp.link(
    rel="stylesheet",
    href="//cdn.rawgit.com/milligram/milligram/master/dist/milligram.min.css",
)
VALID_COLUMN_SIZES = [10, 20, 25, 33, 34, 40, 50, 60, 66, 67, 75, 80, 90, 100]
ROW_ALIGNMENTS = {"top", "bottom", "center", "stretch", "baseline"}


def cdn():
    """
    Provides basic imports from a CDN for miligram.css.

    It adds Roboto font from Google Fonts, and Normalize.css and Miligram.css
    from Rawgit.
    """
    return hp.Block([ROBOTO, NORMALIZE_CSS, MILIGRAM_CSS])


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

        ``button`` also accepts additional HTML attributes as keyword arguments.
    """
    classes = ["button"]
    if clear:
        classes.append("button-clear")
    if outline:
        classes.append("button-outline")

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
def container(*children):
    """
    Container root of a grid-based layout. Children are passed as arguments.
    """
    return hp.div(class_="container", children=children)


def row(*children, padding=True, wrap=False, align=None, **kwargs):
    """
    A row that contains several columns as children.

    Args:
        align ({'top', 'bottom', 'center', 'stretch', 'baseline'}):
            Defines the vertical alignment of elements in the row. Each of those
            options can also be passed as a boolean argument as in
            ``row(..., top=True)``.
        padding (bool):
            If set to False, eliminate the padding for cells in the given row.
        wrap (bool):
            If True, allow children to wrap over the next line when overflow.

        ``row`` also accepts additional HTML attributes as keyword arguments.
    """
    options = {"row-no-padding": not padding, "row-wrap": wrap}
    options.update((k, kwargs[k]) for k in ROW_ALIGNMENTS.intersection(kwargs))
    classes = ["row"]
    classes.extend(cls for cls, on in options.items())

    if align is not None:
        if align not in ROW_ALIGNMENTS:
            raise ValueError(f"invalid alignment: {align!r}")
        classes.append(f"row-{align}")
    return hp.div(class_=classes, children=children, **kwargs)


def column(
    *children,
    size=None,
    offset=None,
    top=False,
    bottom=False,
    center=None,
    align=None,
    **kwargs,
):
    """
    A single column inside a flexible row.

    Args:
        size ({ 10, 20, 25, 33, 34, 40, 50, 60, 66, 67, 75, 80, 90, 100 }):
            Column size (in %). Only a few pre-determined sizes are accepted.
        offset (int):
            Column offset. It accepts the save values as size.
        align {'top', 'bottom', 'center'}:
            Defines the horizontal alignment of elements in a cell. Each of those
            options can also be passed as a boolean argument as in
            ``column(..., top=True)``.

        ``column`` also accepts additional HTML attributes as keyword arguments.
    """
    classes = ["column"]

    # Size
    if size is not None:
        if size not in VALID_COLUMN_SIZES:
            raise ValueError("Invalid size: %s" % size)
        classes.append(f"column-{size:d}")
    if offset:
        if offset not in VALID_COLUMN_SIZES:
            raise ValueError("Invalid offset: %s" % size)
        classes.append(f"column-offset-{offset:d}")

    # Alignment
    if align is not None:
        if align not in ("top", "bottom", "center"):
            raise ValueError(f"invalid alignment: {align!r}")
        classes.append(f"column-{align}")
    elif top:
        classes.append("column-top")
    elif bottom:
        classes.append("column-bottom")
    elif center:
        classes.append("column-center")

    return hp.div(children, **kwargs).add_class(classes)
