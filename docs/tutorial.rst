.. module:: hyperpython

========
Tutorial
========

A simple example
================

Suppose we want to implement a little Bootstrap element that shows a menu with
actions (this is a random example taken from Bootstrap website).

.. code-block:: html

    <div class="btn-group">
      <button type="button"
              class="btn btn-default dropdown-toggle"
              data-toggle="dropdown"
              aria-haspopup="true"
              aria-expanded="false">
        Action <span class="caret"></span>
      </button>
      <ul class="dropdown-menu">
        <li><a href="#">Action</a></li>
        <li><a href="#">Another action</a></li>
        <li><a href="#">Something else here</a></li>
        <li role="separator" class="divider"></li>
        <li><a href="#">Separated link</a></li>
      </ul>
    </div>

Of course we could translate this directly into Hyperpython by calling the
corresponding ``div()``, ``button()``, etc functions. But first, let us break
up this mess into smaller pieces.

.. code-block:: python

    from hyperpython import button, div, p, ul, li, span, a, classes

    def menu_button(name, caret=True, class_=None, **kwargs):
        if caret:
            children = [name, ' ', span('caret')]
        else:
            children = [name]

        return \
            button(
                type='button',
                class_=['btn', 'btn-default', 'dropdown-toggle', *classes(class_)],
                data_toggle="dropdown",
                aria_haspopup="true",
                aria_expanded="false",
                children=children,
                **kwargs
            )

It might look like it's a lot of trouble for a simple component. But now we can
reuse this piece easily instead of writing a similar code from scratch every time
a new button is necessary: ``menu_button('File'), menu_button('Edit'), ...``.
The next step is to create a function that takes a list of strings and return
the corresponding menu (in the real world we might also want to control the href
attribute). We are also going to be clever and use Ellipsis (``...``) as
a menu separator.

.. code-block:: python

    def menu_data(values):
        def do_item(x):
            if x is ...:
                return li(role='separator', class_='divider')
            else:
                # This could parse the href from string, or take a tuple
                # input, or whatever you like. The hyperpython.components.hyperlink
                # function can be handy here.
                return li(a(x, href='#'))
        return ul(map(do_item, values), class_='dropdown-menu')

Now we glue both together...

.. code-block:: python

    def menu(name, values, caret=True):
        return \
            div(class_='btn-group')[
                menu_button(name, caret=True),
                menu_data(values),
            ]

... and create as many new menu buttons as we like:

.. code-block:: python

    menubar = \
        div(id='menubar')[
            menu('File', ['New', 'Open', ..., 'Exit']),
            menu('Edit', ['Copy', 'Paste', ..., 'Preferences']),
            menu('Help', ['Manual', 'Topics', ..., 'About']),
        ]

Look how nice it is now :)


How does it work?
=================

Hyperpython syntax is just regular Python wrapped in a HTML-wannabe DSL. How
does it work?

Take the example:

.. code-block:: python

    element = \
        div(class_="contact-card")[
            span("john", class_="contact-name"),
            span("555-1234", class_="contact-phone"),
        ]

In Hyperpython, we can declare attributes as keyword arguments and children as a
index access. This clever abuse of Python syntax is good for creating expressive
representations of HTML documents. Under the hood, Python calls div() and
generates an :class:`Element` instance. Indexing is used to insert the given
elements as children and then return the tag itself as a result. We encourage
using this syntax only during element creation in order to avoid confusion.

Tag functions also accept a few alternative signatures:

``h1('title')``:
    First positional argument can be a single child, string or list of children.
    This generates ``<h1>title</h1>``.
``h1({'class': 'foo'}, 'title')``:
    If the first argument is a dictionary, it is interpreted as attributes.
    Notice that when passed this way, attribute names are not modified.
    This generates ``<h1 class="foo">title</h1>``.
``h1('title', class_='foo', data_foo=True)``:
    Keyword arguments receive a special treatment: trailing underscores are
    removed from names that conflict with Python keywords and underscores in the
    middle of the word are converted to dashes.
    This generates ``<h1 class="foo" data-foo>title</h1>``.
``h1(class_='foo', children=['title'])``:
    Children can also be passed as a keyword argument.
    This generates ``<h1 class="foo">title</h1>``.

In HTML, all tag attributes are all stringly typed. This is far from ideal and can
be easily fixed since we are representing HTML from a typed language.
Hyperpython does the following coercions when interpreting attributes:

"class" attribute:
    Hyperpython expects a list of strings. If a single string is given, it is
    split into several classes and saved as a list. It has a similar semantics as
    the classList attribute in the DOM.
    The list of classes can also be passed as a dictionary. In that case, it
    includes all keys associated to a truthy value.
boolean attributes:
    A value of False or None for an attribute means that it should be omitted
    from generated HTML. A value of True renders the attribute without the
    associated value.


Imperative interface
--------------------

We encourage users to adopt the declarative API and generally treat tags
as immutable structures. Hyperpython does not enforce immutability and actually
offers some APIs to change data structures inplace. Once a tag is created, it
is possible to change it's attributes dictionary and list of children. There
are also a few methods designed to manipulate Hyperpython data structures.

>>> elem = div('foo', class_='elem')
>>> elem.add_child('bar')
h('div', {'class': ['elem']}, ['foo', 'bar'])

Attributes are also exposed in the .attrs dictionary:

>>> elem.attrs['data-answer'] = 42
>>> elem.attrs.keys()
dict_keys(['class', 'data-answer'])

The "class" and "id" attributes are also exposed directly from the tag object
since they are used so often:

>>> elem = div('foo', class_='class', id='id')
>>> elem.id, elem.classes
('id', ['class'])

Classes can be manipulated directly, but it is safer to use the
``elem.add_class()`` and ``elem.set_class()`` methods, since they understand
all the different ways Hyperpython uses to specify a list of classes.

>>> elem.add_class('bar baz')                               # doctest: +ELLIPSIS
h(...)
>>> print(elem)
<div class="class bar baz" id="id">foo</div>

Notice that add_class() returns the changed element and hence can be used in a
fluid API style.
