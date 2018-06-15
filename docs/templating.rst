==========
Templating
==========

The goal of ``hyperpython`` is to replace a template engine such as Jinja2 by
Python code that generates HTML fragments. This approach removes the constraints
imposed by the template language and makes integration with surrounding Python
code trivial.

I know you are probably thinking: *"it is a really bad idea to mix template with
logic"*. Hyperpython obviously doesn't prevent you from shooting yourself on the foot
and you can make really messy code if you want. However, things can be very
smooth if you stick to focused and simple components that adopt a more
functional style.

Our advice is: *break your code in small pieces and compose these pieces in
simple and predictable ways*. Incidentally, this is a good advice for any form
of code ;).

The fact is that our good old friend *"a function"* is probably simpler to use
and composes much better than anything a templating engine has come up with.

Let us dive in!

We want to implement a little Bootstrap element that shows a menu with actions
(this is a random example taken from Bootstrap website).

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

Of course we could translate this directly into hyperpython code by calling the
corresponding ``div()``'s, ``button()``'s, etc. But first, let us break up this
mess into smaller pieces.

.. code-block:: python

    from hyperpython import button, div, p, ul, li, span, a

    def menu_button(name, caret=True):
        return \
            button(
                type='button',
                class_='btn btn-default dropdown-toggle',
                data_toggle="dropdown",
                aria_haspopup="true",
                aria_expanded="false",
                children=[
                    name,
                    span(class_='caret') if caret else None,  # Nones are ignored
                ],
            )

Ok, it looks like it's a lot of trouble for a simple component. But now we can
reuse this piece and easily make as many buttons as we like: ``menu_button('File'), menu_button('Edit'), ...``.
The next step is to create a function that takes a list of strings and return
the corresponding menu (in the real world we might also want to control the href
attribute). We are also going to be clever and use the Ellipsis (``...``) as
a menu separator.

.. code-block:: python

    def menu_data(values):
        def do_item(x):
            if x is ...:
                return li(role='separator', class_='divider')
            else:
                # This could parse the href from string, or take a tuple
                # input, or whatever you like. The hyperpython.helpers.link function
                # can be handy here.
                return li(a(x, href='#'))

        return \
            ul(class_='dropdown-menu')[
                map(do_item, values)
            ]

We glue both together...

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

Hyperpython HTML syntax is obviously just regular Python wrapped in a HTML-wannabe
DSL. How does it work?

Take the example:

.. code-block:: python

    element = \
        div(class_="contact-card")[
            span("john", class_="contact-name"),
            span("555-1234", class_="contact-phone"),
        ]

The first positional argument is a single child element or a list of children.
Keyword arguments are interpreted as tag attributes. Notice we did not use
``class`` as an argument name because it is a reserved keyword in Python.
Hyperpython, however, ignores all trailing underscores and converts underscores in
the middle of the argument to dashes.

If your tag uses underscore in any attribute name or if you happen to have the
attributes to values stored in a dictionary, just use the ``attrs`` argument
of a tag constructor.

.. code-block:: python

    # <div my_attr="1" attrs="2" data-attr="3">foo</div>

    div('foo', attrs={'my_attr': 1, 'attrs': 2}, data_attr=3)


Functional API
--------------



Imperative API
--------------

The contact-card element above could have been created in a more regular
imperative fashion::

    element = div(class_="contact-card")
    span1 = span("john", class_="contact-name")
    span2 = span("555-1234", class_="contact-phone")
    element.children.extend([span1, span2])

This is not as expressive as the first case and forces us to think *imperative*
instead of thinking in *declarative markup*. This is not very natural for HTML
and also tends to be more verbose. The "square bracket syntax" is just regular
Python indexing syntax abused to call ``.children.extend`` to insert child
elements into the tag's children attribute.

More specifically, the ``tag[args]`` creates a copy of the original tag, flatten
all list and tuple arguments, insert them into the copied object, and return it.
The same hack is applied to the metaclass and this allow us to call tags that do
not define any attribute like this:

.. code-block:: python

    element = \
        div[
            span('Foo'),
            span('Bar'),
        ]

And since lists, tuples, mappings, and generators are flattened, we can also
define a tag's children with list comprehensions and maps:

.. code-block:: python

    words = ['name1', 'name2']
    urls = ['url1', 'url2']
    element = \
        div([
            *[span(x) for x in words],
            *map(lambda x, y: a(x, href=y), words, urls),
        ])

Since square brackets were already taken to define the children elements of a
tag, we cannot use them to directly access the children elements of a tag.
Instead, this must be done explicitly using the ``tag.children`` interface.
It behaves just as a regular list so you can do things as

>>> elem = div('foo', class_='elem')
>>> elem.add_child('Hello world')
>>> first = elem.children.pop(0)
>>> print(elem)
<div class="elem">Hello world</div>

Similarly to children, attributes are also exposed in a special attribute named
`attrs` that behaves like a dictionary:

>>> elem = div('foo', class_='elem')
>>> elem.attrs['data-answer'] = 42
>>> elem.attrs.keys()
dict_keys(['class', 'data-answer'])

The attrs dictionary also exposes the ``id`` and ``class`` elements as read-only
values. ``id`` is also exposed as an attribute and ``class`` is constructed from
the list of classes in the ``tag.classes`` attribute.

>>> elem = div('foo', class_='class', id='id')
>>> elem.id, elem.classes
('id', ['class'])
>>> elem.id = 'new-id'
>>> print(elem)
<div class="class" id="new-id">foo</div>
