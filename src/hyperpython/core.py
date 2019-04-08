import copy
import io
import json
from collections.abc import Sequence

from markupsafe import Markup
from sidekick import lazy, delegate_to
from types import MappingProxyType

from .helpers import classes
from .renderers import dump_attrs, render_pretty
from .utils import escape as _escape

# https://www.w3.org/TR/html5/syntax.html#void-elements
VOID_ELEMENTS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "keygen",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}
SEQUENCE_TYPES = (tuple, list, type(x for x in []), type(map(lambda: 0, [])))
JUPYTER_NOTEBOOK_RENDER_HTML = True
cte = lambda value: lambda *args: value


class BaseElement:
    """
    Mixins for the Element API.
    """

    # Default values and properties
    tag = property(cte(None))
    attrs = MappingProxyType({})
    classes = property(lambda self: self.attrs.get("class", []))
    id = property(lambda self: self.attrs.get("id"))

    @id.setter
    def id(self, value):
        setitem = getattr(self.attrs, "__setitem__", None)
        if setitem is None:
            raise AttributeError("cannot set id of immutable type")
        setitem("id", value)

    children = ()
    requires = ()

    is_element = False
    is_void = False

    def __html__(self):
        return self.render()

    def __str__(self):
        return str(self.__html__())

    def _repr_html_(self):
        return self.__html__() if JUPYTER_NOTEBOOK_RENDER_HTML else repr(self)

    def _repr_child(self):
        return self.__repr__()

    def render(self):
        """
        Renders object as string.
        """
        file = io.StringIO()
        self.dump(file)
        return file.getvalue()

    def dump(self, file):
        """
        Dump contents of element in the given file.
        """
        raise NotImplementedError

    def json(self):
        raise NotImplementedError

    def copy(self):
        raise NotImplementedError

    def pretty(self, **kwargs):
        """
        Render a pretty printed HTML.

        This method is less efficient than .render(), but is useful for
        debugging
        """
        return render_pretty(self, **kwargs)

    def walk(self):
        """
        Walk over all elements in the object tree, including Elements and
        Text fragments.
        """

        yield self
        for obj in self.children:
            yield from obj.walk()

    def walk_tags(self):
        """
        Walk over all elements in the object tree, excluding Text fragments.
        """

        if self.is_element:
            yield self

        for obj in self.children:
            if obj.is_element:
                yield from obj.walk_tags()

    def add_child(self, value):
        """
        Add child element to data structure.

        Caveat: Hyperpython *do not* enforce immutability, but it is a good
        practice to keep HTML data structures immutable.
        """
        append = getattr(self.children, "append", None)
        if append is None:
            raise TypeError("cannot change immutable structure")
        else:
            append(as_child(value))
        return self


# ------------------------------------------------------------------------------
class Component(BaseElement):
    """
    Component that delegates the creation of HTML tree to an .html() method.
    """

    json = delegate_to("_tree")
    dump = delegate_to("_tree")
    tag = delegate_to("_tree")
    attrs = delegate_to("_tree")
    children = delegate_to("_tree")
    requires = delegate_to("_tree")
    is_void = delegate_to("_tree")
    is_element = delegate_to("_tree")

    @lazy
    def _tree(self):
        return self.html()

    def html(self, **kwargs):
        raise NotImplementedError("must be implemented in subclasses")

    def copy(self):
        new = copy.copy(self)
        new._tree = self._tree.copy()
        return new


# ------------------------------------------------------------------------------
class Element(BaseElement):
    """
    Represents an HTML element.
    """

    tag: str = ""
    attrs: dict
    children: list
    is_void: bool
    is_element = True

    def __init__(
            self, tag: str, attrs: dict, children: list, is_void=False, requires=()
    ):
        self.tag = tag
        self.attrs = {
            k: v
            for k, v in map(as_attr, attrs.keys(), attrs.values())
            if k is not None and v is not None
        }
        self.children = list(map(as_child, children))
        self.is_void = is_void
        self.requires = tuple(requires)

    def __getitem__(self, item):
        if self.is_void:
            raise ValueError("void elements cannot define children")

        if isinstance(item, SEQUENCE_TYPES):
            self.children.extend(map(as_child, item))
        elif item is None:
            pass
        else:
            self.children.append(as_child(item))
        return self

    def __repr__(self):
        attrs = self.attrs
        children = self.children
        if len(children) == 1 and isinstance(children[0], Text):
            children_repr = repr_child(children[0])
        else:
            data = ", ".join(repr_child(x) for x in children)
            children_repr = f"[{data}]"

        if attrs and children:
            return "h(%r, %s, %s)" % (self.tag, attrs, children_repr)
        elif attrs:
            return "h(%r, %s)" % (self.tag, attrs)
        elif children:
            return "h(%r, %s)" % (self.tag, children_repr)
        else:
            return "h(%r)" % self.tag

    def __eq__(self, other):
        if other.__class__ is self.__class__:
            return (
                    self.tag == other.tag
                    and self.attrs == other.attrs
                    and len(self.children) == len(other.children)
                    and all(x == y for x, y in zip(self.children, other.children))
            )
        return NotImplemented

    def dump(self, file):
        """
        Dumps HTML data into file.
        """
        write = file.write
        write("<")
        write(self.tag)
        if self.attrs:
            write(" ")
            pos = file.tell()
            dump_attrs(self.attrs, file)
            if file.tell() == pos:
                file.seek(pos - 1)
        write(">")
        if not self.is_void:
            for child in self.children:
                child.dump(file)
        write(f"</{self.tag}>")

    def json(self):
        """
        JSON-compatible representation of object.
        """
        json = {"tag": self.tag}
        if self.attrs:
            json["attrs"] = self.attrs
        if self.children:
            json["children"] = [x.json() for x in self.children]
        return json

    def copy(self):
        """
        Return a copy of object.
        """
        new = object.__new__(Element)
        new.tag = self.tag
        new.attrs = dict(self.attrs)
        new.children = list(self.children)
        new.is_void = self.is_void
        new.requires = self.requires
        return new

    def add_class(self, cls, first=False):
        """
        Add class or group of classes to the class list.
        """
        new_classes = classes(cls)
        try:
            old_classes = self.attrs["class"]
        except KeyError:
            self.attrs["class"] = list(new_classes)
        else:
            if first:
                new_classes = list(new_classes)
                class_set = set(new_classes)
                new_classes.extend(x for x in old_classes if x not in class_set)
                self.attrs["class"][:] = new_classes
            else:
                class_set = set(old_classes)
                old_classes.extend(x for x in new_classes if x not in class_set)
        return self

    def set_class(self, cls=()):
        """
        Replace all current classes by the new ones.
        """
        self.attrs["class"] = list(classes(cls))
        return self


# ------------------------------------------------------------------------------
class Text(str, BaseElement):
    """
    Represents regular text strings
    """

    def __html__(self):
        return _escape(str(self))

    def __getitem__(self, item):
        raise TypeError("Text elements cannot set children")

    def __repr__(self):
        return "Text(%r)" % str(self)

    def _repr_child(self):
        return repr(str(self))

    def render(self):
        return _escape(self)

    def dump(self, file):
        file.write(_escape(self))

    def copy(self, parent=None):
        return self

    def json(self):
        return {"text": str(self)}


class Blob(Markup, BaseElement):
    """
    A blob of raw HTML data.
    """

    def __init__(self, data):
        Markup.__init__(data)

    def __html__(self):
        return self

    def __getitem__(self, item):
        raise TypeError("HTML Blobs cannot set children")

    def __repr__(self):
        return "Blob(%r)" % str(self)

    def _repr_child(self):
        return repr(self)

    def render(self):
        return self.__html__()

    def dump(self, file):
        file.write(self)

    def copy(self, parent=None):
        return self

    def json(self):
        return {"raw": str(self)}


# ------------------------------------------------------------------------------
class Json(BaseElement):
    """
    Stores JSON data.

    Hyperpython stores the JSON objects as data instead of text blobs. Users can
    introspect the data content in the .data attribute.
    """

    _json_data = lazy(lambda self: json.dumps(self.data))

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return "Json(%r)" % self.data

    def __html__(self):
        return self._json_data

    def dump(self, file):
        json.dump(self.data, file)

    def json(self):
        return self.data

    def copy(self):
        return Json(self.data)


# ------------------------------------------------------------------------------
class Block(BaseElement, Sequence):
    """
    Represents a list of elements *not* wrapped in a tag.
    """

    classes = property(lambda self: [])

    def __init__(self, children, requires=()):
        self.children = list(map(as_child, children))
        self.requires = list(requires)

    def __iter__(self):
        return iter(self.children)

    def __getitem__(self, idx):
        return self.children[idx]

    def __len__(self):
        return len(self.children)

    def dump(self, file):
        for child in self.children:
            child.dump(file)

    def copy(self):
        return Block(list(self.children), requires=list(self.requires))

    def json(self):
        return {"body": [x.to_json() for x in self.children]}


#
# Helper functions
#
def as_attr(name, value):
    """
    Enforces an arbitrary pair of attribute name and value has a compatible
    Hyperpython values.

    Args:
        name: attribute name
        value: attribute value
    """
    if name == "class":
        value = list(classes(value))
        return name, value
    return name, value


def as_child(value):
    """
    Convert arbitrary object to a compatible Element object.
    """

    if isinstance(value, BaseElement):
        return value
    elif isinstance(value, Markup):
        return Blob(value)
    elif isinstance(value, str):
        return Text(value)
    elif isinstance(value, (int, float)):
        return Text(str(value))
    elif isinstance(value, Tag):
        return Element(value.tag, {}, [], value.tag in VOID_ELEMENTS)
    elif hasattr(value, "__html__"):
        return Blob(value.__html__())
    elif hasattr(value, "__hyperpython__"):
        return value.__hyperpython__()
    elif isinstance(value, list):
        return Block(value)
    else:
        data = str(value)
        if data == value:
            return Text(data)
        type_name = value.__class__.__name__
        raise TypeError("invalid type for a child node: %s" % type_name)


def repr_child(value):
    """
    Simplify representation of element, when it is inside a list of children.
    """
    # noinspection PyProtectedMember
    return value._repr_child()


class Tag:
    """
    Return an HTMLTag subclass for the given tag.
    """

    _h_function: callable

    def __init__(self, tag, help_text=None):
        self.tag = tag
        self.__doc__ = help_text

    def __call__(self, *args, **kwargs):
        try:
            h = self._h_function
        except AttributeError:
            from .tags import h
            Tag._h_function = h
        return h(self.tag, *args, **kwargs)

    def __getitem__(self, item):
        return self._h_function(self.tag)[item]


