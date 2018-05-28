import io
from types import MappingProxyType

from markupsafe import Markup

from .renderers import dump_attrs, render_pretty
from .utils import flatten, unescape, escape as _escape

SEQUENCE_TYPES = (tuple, list, type(x for x in []))


class ElementMixin:
    """
    Mixins for the Element API.
    """

    # Default values and properties
    tag = None
    attrs = MappingProxyType({})
    classes = property(lambda self: self.attrs.get('class', []))
    id = property(lambda self: self.attrs.get('id'))

    children = ()
    requires = ()

    is_element = False
    is_void = False

    def render(self, **kwargs):
        """
        Render element as string.
        """
        raise NotImplementedError

    def json(self):
        raise NotImplementedError

    def copy(self):
        raise NotImplementedError

    def pretty(self):
        """
        Render a pretty printed HTML.

        This method is less efficient than .render(), but is useful for
        debugging
        """
        return render_pretty(self)

    def walk(self):
        """
        Walk over all elements in the object tree, including Elements and
        Text fragments.
        """

        yield self
        for obj in self.children:
            yield obj
            if obj.is_element:
                yield from (child.walk() for child in obj.children)

    def walk_tags(self):
        """
        Walk over all elements in the object tree, excluding Text fragments.
        """

        if not self.is_element:
            return

        yield self
        for obj in self.children:
            if obj.is_element:
                yield obj
                yield from (child.walk_tags() for child in obj.children)


# ------------------------------------------------------------------------------
class Element(ElementMixin):
    """
    Represents an HTML element.
    """

    tag: str
    attrs: dict
    children: list
    is_void: bool
    is_element = True

    def __init__(self, tag: str, attrs: dict, children: list, is_void=False,
                 requires=()):
        self.tag = tag
        self.attrs = {
            k: v for k, v in map(as_attr, attrs.keys(), attrs.values())
            if k is not None and v is not None
        }
        self.children = list(map(as_child, children))
        self.is_void = is_void
        self.requires = tuple(requires)

    def __getitem__(self, item):
        if self.is_void:
            raise ValueError('void elements cannot define children')

        if isinstance(item, SEQUENCE_TYPES):
            children = flatten(item)
        elif item is None:
            children = []
        else:
            children = [item]
        return Element(self.tag, self.attrs, children, False, self.requires)

    def __str__(self):
        return str(self.__html__())

    def __repr__(self):
        attrs = self.attrs
        children = self.children
        requires = self.requires
        if attrs and children:
            return 'h(%r, %r, %r)' % (self.tag, self.attrs, self.children)
        elif attrs:
            return 'h(%r, %r)' % (self.tag, attrs)
        elif children:
            return 'h(%r, %r)' % (self.tag, children)
        else:
            return 'h(%r)' % self.tag

    def __html__(self):
        return self.render()

    def __eq__(self, other):
        if other.__class__ is self.__class__:
            return \
                self.tag == other.tag and \
                self.attrs == other.attrs and \
                len(self.children) == len(other.children) and \
                all(x == y for x, y in zip(self.children, other.children))
        return NotImplemented

    def dump(self, file):
        """
        Dumps HTML data into file.
        """
        write = file.write
        write('<')
        write(self.tag)
        if self.attrs:
            write(' ')
            dump_attrs(self.attrs, file)
        write('>')
        if not self.is_void:
            for child in self.children:
                child.dump(file)
        write(f'</{self.tag}>')

    def render(self):
        """
        Renders object as string.
        """
        file = io.StringIO()
        self.dump(file)
        return file.getvalue()

    def json(self):
        """
        JSON-compatible representation of object.
        """
        json = {'tag': self.tag}
        if self.attrs:
            json['attrs'] = self.attrs
        if self.children:
            json['children'] = [x.json() for x in self.children]
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

    def add_class(self, *classes):
        """
        Add classes to the class list.

        Does nothing if class is already present.
        """
        try:
            self.attrs['class'].extend(classes)
        except KeyError:
            self.attrs['class'] = list(classes)


# ------------------------------------------------------------------------------
class Text(Markup, ElementMixin):
    """
    It extends the Markup object with a Element-compatible API.
    """

    id = None
    classes = property(lambda self: [])
    unescaped = property(unescape)

    def __new__(cls, data, escape=None):
        return super().__new__(cls, data)

    def __init__(self, data, escape=None):
        if escape is None:
            escape = not isinstance(data, Markup)
        if escape and isinstance(data, Markup):
            escape = False
        self.escape = escape

    def __html__(self):
        if self.escape:
            return _escape(str(self))
        return self

    def __getitem__(self, item):
        raise TypeError('Text elements cannot set children')

    def __repr__(self):
        return 'Text(%r)' % str(self)

    def render(self):
        return self.__html__()

    def dump(self, file):
        if self.escape:
            file.write(_escape(self))
        else:
            file.write(self)

    def copy(self, parent=None):
        return Text(self)

    def json(self):
        return {'text': str(self)} if self.escape else {'raw': str(self)}


#
# Helper functions
#
def as_attr(name, value):
    """
    Convert arbitrary object to a valid value for an Element attribute.

    Args:
        name: attribute name
        value: attribute value
    """
    if name == 'class':
        if isinstance(value, str):
            return name, value.split(' ')
    return name, value


def as_child(value):
    """
    Convert arbitrary object to a compatible Element object.
    """
    if isinstance(value, (Element, Text)):
        return value
    elif isinstance(value, (str, Markup)):
        return Text(value)
    elif isinstance(value, (int, float)):
        return Text(str(value))
    elif isinstance(value, Tag):
        return Tag._h_function(value.tag)
    elif hasattr(value, '__html__'):
        return Text(Markup(value.__html__()), escape=False)
    else:
        type_name = value.__class__.__name__
        raise TypeError('invalid type for a child node: %s' % type_name)


class Tag:
    """
    Return an HTMLTag subclass for the given tag.
    """
    _h_function = None

    def __init__(self, tag, help_text=None):
        self.tag = tag
        self.__doc__ = help_text

    def __call__(self, *args, **kwargs):
        return self._h_function(self.tag, *args, **kwargs)

    def __getitem__(self, item):
        return self._h_function(self.tag)[item]
