from .core import Tag, Element, Text, as_child, as_attr, SEQUENCE_TYPES, VOID_ELEMENTS
from .utils import html_safe_natural_attr


def h(tag, *args, children=None, **attrs):
    """
    Creates a tag.

    It has many different signatures:

    h('h1', 'content')
        Content can be a string, a child node or a list of children.

    h('h1', {'class': 'title'}, 'content')
        If the second argument is a dictionary, it is interpreted as tag
        attributes.

    h('h1', 'title', class_='title')
        Keyword arguments are also interpreted a attributes. The h function
        makes a few changes: underscores are converted to dashes and trailing
        underscores after Python keywords such as ``class_``, ``for_``, etc are
        ignored.

    h('h1', class_='title')['content']
        Children can also be specified using squared brackets. It understands
        strings, other tags, and lists of tags.

    h('h1', class_='title', children=['content'])
        Optionally, the list of children nodes can be specified as a keyword
        argument.
    """
    attr_name = html_safe_natural_attr
    is_void = tag in VOID_ELEMENTS
    n_args = len(args)
    attrs = dict(as_attr(attr_name(k), v) for k, v in attrs.items())

    # Children can be set explicitly as a keyword argument since there is no
    # "children" attribute in html. This makes the API closer to other VDOM libs
    # in Js such as React.
    if children is not None:
        if args:
            raise TypeError(
                "cannot positional arguments if children is specified by a"
                "keyword argument"
            )
        args = (attrs, _as_children(children))
        n_args = 2
    if n_args == 0:
        children = []
    elif n_args == 1:
        arg, = args
        if isinstance(arg, dict):
            attrs.update(as_attr(k, v) for k, v in attrs.items())
            children = []
        else:
            children = _as_children(arg)
    elif n_args == 2:
        attrs.update(as_attr(k, v) for k, v in args[0].items())
        children = _as_children(args[1])
    else:
        raise TypeError("h() accepts at most 3 positional arguments")

    return Element(tag, attrs, children, is_void)


def _as_children(data):
    if isinstance(data, str):
        return [Text(data)]
    elif isinstance(data, Element):
        return [data]
    elif isinstance(data, SEQUENCE_TYPES):
        return list(map(as_child, data))
    else:
        return [as_child(data)]


Tag._h_function = staticmethod(h)

# Basic document structure
HTML5 = document = Tag("html", "The root of an HTML document")
body = Tag("body", "The document's body")
head = Tag("head", "Information about the document")

# Meta information (tags that appear under <head>
meta = Tag("meta", "Defines metadata about an HTML document")
link = Tag("link", "Relationship with and an external resource")
title = Tag("title", "A title for the document")

# Generic tags
div = Tag("div", "A section in a document (block)")
span = Tag("span", "A section in a document (text)")

# Structural tags
article = Tag("article", "An article")
aside = Tag("aside", "Content aside from the page content")
details = Tag("details", "Details that the user can view or hide")
footer = Tag("footer", "A footer for a document or section")
figcaption = Tag("figcaption", "A caption for a <figure> element")
figure = Tag("figure", "Specifies self-contained content")
header = Tag("header", "A header for a document or section")
main = Tag("main", "Specifies the main content of a document")
p = Tag("p", "A paragraph")
pre = Tag("pre", "Pre-formatted text")
section = Tag("section", "A section in a document")

# External elements
embed = Tag("embed", "A container for an external (non-HTML) application")
iframe = Tag("iframe", "An inline frame")
noscript = Tag("noscript", "Content for users that do not support scripts")
object_ = Tag("object", "An embedded object")
script = Tag("script", "A client-side script")
style = Tag("style", "Defines style information for a document")

# Forms
button = Tag("button", "A clickable button")
fieldset = Tag("fieldset", "Groups related elements in a form")
form = Tag("form", "An HTML form for user input")
input_ = Tag("input", "An input control")
keygen = Tag("keygen", "A key-pair generator field")
label = Tag("label", "A label for an <input> element")
legend = Tag("legend", "A caption for a <fieldset> element")
optgroup = Tag("optgroup", "A group of related <option>'s")
option = Tag("option", "An option in a drop-down list")
select = Tag("select", "A drop-down list")
textarea = Tag("textarea", "A multiline input control")

# Headings
h1 = Tag("h1", "Defines HTML heading")
h2 = Tag("h2", "Defines HTML heading")
h3 = Tag("h3", "Defines HTML heading")
h4 = Tag("h4", "Defines HTML heading")
h5 = Tag("h5", "Defines HTML heading")
h6 = Tag("h6", "Defines HTML heading")

# Lists/description lists
dd = Tag("dd", "A value of a term in a description list")
dl = Tag("dl", "A description list")
dt = Tag("dt", "A term/name in a description list")
ul = Tag("ul", "An unordered list")
li = Tag("li", "A list item")
ol = Tag("ol", "An ordered list")

# Multimedia and images
area = Tag("area", "An area inside an image-map")
audio = Tag("audio", "Defines sound content")
canvas = Tag("canvas", "Draw graphics via scripting")
img = Tag("img", "An image")
picture = Tag("picture", "A container for multiple image resources")
track = Tag("track", "Text tracks for media elements (<video> and <audio>)")
video = Tag("video", "A video or movie")
source = Tag("source", "Media resources for video/audio elements")

# Navigation
a = Tag("a", "A hyperlink")
menu = Tag("menu", "A list/menu of commands")
menuitem = Tag("menuitem", "An item on a popup menu")
nav = Tag("nav", "Defines navigation links")

# Roles
abbr = Tag("abbr", "An abbreviation or an acronym")
blockquote = Tag("blockquote", "Section quoted from another source")
code = Tag("code", "A piece of computer code")

# Tables
caption = Tag("caption", "A table caption")
col = Tag("col", "Specifies a column within a <colgroup>")
colgroup = Tag("colgroup", "Group of columns in a table")
table = Tag("table", "A table")
tbody = Tag("tbody", "Groups the body content in a table")
td = Tag("td", "A cell in a table")
tfoot = Tag("tfoot", "Groups the footer content in a table")
th = Tag("th", "A header cell in a table")
thead = Tag("thead", "Groups the header content in a table")
tr = Tag("tr", "A row in a table")

# Text roles and styling
b = Tag("b", "Bold text")
em = Tag("em", "Emphasized text")
del_ = Tag("del", "Text that has been deleted from a document")
i = Tag("i", "A part of text in an alternate voice or mood")
ins = Tag("ins", "A text that has been inserted into a document")
mark = Tag("mark", "Defines marked/highlighted text")
q = Tag("q", "A short quotation")
s = Tag("s", "Text that is no longer correct")
small = Tag("small", "Defines smaller text")
strong = Tag("strong", "Important text")
sub = Tag("sub", "Subscripted text")
sup = Tag("sup", "Superscripted text")
u = Tag("u", "Marks stylistically different text")

# Textual breaks
br = Tag("br", "A single line break")
hr = Tag("hr", "A thematic change in the content")
wbr = Tag("wbr", "A possible line-break")

# Typographical and text annotations for different languages
bdi = Tag("bdi", "Isolates text with a possible different direction")
bdo = Tag("bdo", "Overrides the current text direction")
rp = Tag("rp", "Text for browsers that do not support ruby annotations")
rt = Tag("rt", "Explanation/pronunciation of characters")
ruby = Tag("ruby", "A ruby annotation (for East Asian typography)")

# Uncategorized tags
address = Tag("address", "Contact information for the owner of a document")
dialog = Tag("dialog", "A dialog box or window")
base = Tag("base", "Base URL/target for all relative URLs in a document")
cite = Tag("cite", "The title of a work")
datalist = Tag("datalist", "A list of pre-defined options for input controls")
dfn = Tag("dfn", "Represents the defining instance of a term")
kbd = Tag("kbd", "Defines keyboard input")
map_ = Tag("map", "A client-side image-map")
meter = Tag("meter", "A scalar measurement within a known range (a gauge)")
param = Tag("param", "A parameter for an object")
progress = Tag("progress", "Represents the progress of a task")
samp = Tag("samp", "Defines sample output from a computer program")
summary = Tag("summary", "A visible heading for a <details> element")
time = Tag("time", "A date/time")
var = Tag("var", "A variable")
output = Tag("output", "The result of a calculation")

# Deprecated tags. Only valid in HTML4
acronym = Tag("acronym", "Use <abbr> instead. An acronym")
applet = Tag("applet", "Use <embed> or <object> instead. An embedded applet")
big = Tag("big", "Use CSS instead. Defines big text")
basefont = Tag("basefont", "Specifies a font for all text in a document")
center = Tag("center", "Defines centered text")
dir_ = Tag("dir", "Use <ul> instead. A directory list")
font = Tag("font", "Defines font, color, and size for text")
frame = Tag("frame", "A window (a frame) in a frameset")
frameset = Tag("frameset", "A set of frames")
noframes = Tag("noframes", "Content for users that do not support frames")
strike = Tag("strike", "Use <del> or <s> instead. Defines strikethrough text")
tt = Tag("tt", "Use CSS instead. Teletype text")
