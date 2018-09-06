import io
from collections import Sequence
from types import MappingProxyType

from markupsafe import Markup

from .helpers import classes
from .renderers import dump_attrs, render_pretty
from .utils import unescape, escape as _escape

SEQUENCE_TYPES = (tuple, list, type(x for x in []), type(map(lambda: 0, [])))


class ElementMixin:
    """
    Mixins for the Element API.
    """

    # Default values and properties
    tag = None
    attrs = MappingProxyType({})
    classes = property(lambda self: self.attrs.get('class', []))
    id = property(lambda self: self.attrs.get('id'))

    @id.setter
    def id(self, value):
        self.attrs['id'] = value

    children = ()
    requires = ()

    is_element = False
    is_void = False

    def _repr_html_(self):
        return self.__html__()

    def _repr_child_(self):
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

    def add_child(self, value):
        """
        Add child element to data structure.

        Caveat: Hyperpython *do not* enforce immutability, but it is a good
        practice to keep HTML data structures immutable.
        """
        try:
            append = self.children.append
        except AttributeError:
            raise TypeError('cannot change immutable structure')
        else:
            append(as_child(value))


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
            self.children.extend(map(as_child, item))
        elif item is None:
            pass
        else:
            self.children.append(as_child(item))
        return self

    def __str__(self):
        return str(self.__html__())

    def __repr__(self):
        attrs = self.attrs
        children = self.children
        if len(children) == 1 and isinstance(children[0], Text):
            children_repr = children[0]._repr_child_()
        else:
            data = ', '.join(x._repr_child_() for x in children)
            children_repr = f'[{data}]'

        if attrs and children:
            return 'h(%r, %s, %s)' % (self.tag, attrs, children_repr)
        elif attrs:
            return 'h(%r, %s)' % (self.tag, attrs)
        elif children:
            return 'h(%r, %s)' % (self.tag, children_repr)
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
            pos = file.tell()
            dump_attrs(self.attrs, file)
            if file.tell() == pos:
                file.seek(pos - 1)
        write('>')
        if not self.is_void:
            for child in self.children:
                child.dump(file)
        write(f'</{self.tag}>')

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

    def add_class(self, cls, first=False):
        """
        Add class or group of classes to the class list.
        """
        new_classes = classes(cls)
        try:
            old_classes = self.attrs['class']
        except KeyError:
            self.attrs['class'] = new_classes
        else:
            if first:
                class_set = set(new_classes)
                new_classes.extend(x for x in old_classes if x not in class_set)
                self.attrs['class'][:] = new_classes
            else:
                class_set = set(old_classes)
                old_classes.extend(x for x in new_classes if x not in class_set)
        return self

    def set_class(self, cls):
        """
        Replace all current classes by the new ones.
        """
        self.attrs['class'] = list(classes(cls))
        return self


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

    def _repr_child_(self):
        if self.escape:
            return repr(str(self))
        else:
            return repr(self)

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


class Block(ElementMixin, Sequence):
    """
    Represents a list of elements *not* wrapped in a tag.
    """

    id = None
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
        return {'body': [x.to_json() for x in self.children]}


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
    if name == 'class':
        value = list(classes(value))
        return name, value
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
        return Text(value.__html__(), escape=False)
    elif hasattr(value, '__hyperpython__'):
        return value.__hyperpython__()
    else:
        data = str(value)
        if data == value:
            return Text(data)
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
