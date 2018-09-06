.. image:: https://readthedocs.org/projects/hyperpython/badge/?version=latest
    :target: http://hyperpython.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. image:: https://travis-ci.org/fabiommendes/hyperpython.svg?branch=master
    :target: https://travis-ci.org/fabiommendes/hyperpython
    :alt: Build status
.. image:: https://codeclimate.com/github/fabiommendes/hyperpython/badges/gpa.svg
    :target: https://codeclimate.com/github/fabiommendes/hyperpython
    :alt: Code Climate
.. image:: https://codecov.io/gh/fabiommendes/hyperpython/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/fabiommendes/hyperpython
    :alt: Code coverage
.. module:: hyperpython


Hyperpython
===========

Hyperpython is a Python interpretation of Hyperscript_. If you are not
familiar with Hyperscript, think of it as a pure Javascript alternative to JSX.
Hyperpython allow us to generate, manipulate and query HTML documents using a
small DSL embedded in Python. Just like Hyperscript, the default entry point is
the :func:`hyperpython.h` function:

>>> from hyperpython import h
>>> elem = h('p', {'class': 'hello'}, ['Hello World!'])

.. _Hyperscript: https://github.com/hyperhype/hyperscript

This can be converted to HTML by calling ``str()`` on the element:

>>> print(elem)
<p class="hello">Hello World!</p>

It accepts Hyperscript's ``h(tag, attributes, list_of_children)`` signature,
but we encourage to use more idiomatic Python version that uses keyword arguments to
represent attributes instead of a dictionary. If the list of children contains a
single element, we can also omit the brackets:

>>> h('p', 'Hello World!', class_='hello') == elem
True

Notice in the snippet above that we had to escape the "class" attribute because
it is a reserved word in Python. Hyperpython maps Python keyword arguments by replacing
underscores with dashes and by escaping Python reserved words such as "class", "for"
"from", etc with a trailing underscore.

Elements can be be more conveniently created with standalone functions representing
specific tags:

>>> print(p('Hello World!', class_='hello'))
<p class="hello">Hello World!</p>

In Python, keyword arguments cannot appear after positional arguments. This means
that attributes are placed *after* the list of children, which isn't natural to
represent HTML. For simple elements like the ones above, it does not hinders
legibility, but for larger structures it can be a real issue. Hyperpython
provides two alternatives. The first uses the index notation:


>>> from hyperpython import div, p, h1
>>> fragment = \
...     div(class_="alert-box")[
...         h1('Hello Python'),
...         p('Now you can write HTML in Python!'),
...     ]

The second alternative is to use the "children" pseudo-attribute. This is the
approach taken by some Javascript libraries such as React:

>>> fragment = \
...     div(class_="alert-box",
...         children = [
...             h1('Hello Python'),
...             p('Now you can write HTML in Python!'),
...         ])


Hyperpython returns a DOM-like structure which we can introspect, query and
modify later. The main usage, of course, is to render strings of HTML source
code. We expect that the main use of Hyperpython will be to complement (or even replace)
the templating language in a Python web application. That said, Hyperpython generates a
very compact HTML that is efficient to generate and transmit over the wire. To
get a more human-friendly output (and keep your sanity while debugging), use
the .pretty() method:

>>> print(fragment.pretty())
<div class="alert-box">
  <h1>Hello Python</h1>
  <p>Now you can write HTML in Python!</p>
</div>
<BLANKLINE>


Replacing templates
===================

The goal of ``hyperpython`` is to replace a lot of work that would be traditionally
done with a template engine such as Jinja2 by Python code that generates HTML
fragments. Templating languages are obviously more expressive than pure Python for
string interpolation, and are a perfect match for ad hoc documents. For large systems,
they offer little in terms of architecture, organization and code reuse.

A recent trend in Javascript is to promote direct creation of DOM or
virtual DOM nodes sidestepping the whole business of rendering intermediate
HTML strings. React was probably the library that better popularized this idea. As they
nicely put, "Templates separate technologies, not concerns". There is no point
on choosing a deliberately underpowered programming language that integrates
poorly with your data sources just to output structured documents in a flat string
representation.

The same lesson can be applied to Python on the server side. With Hyperpython,
we can generate HTML directly in Python. Hyperpython plays nicely with
existing templating systems, but it makes easy to migrate parts of your rendering
sub-system to Python.

For those afraid of putting too much logic on templates, we recognize that
Hyperpython doesn't prevent anyone from shooting themselves on the foot, but neither
do any minimally powerful templating engine. It always requires some discipline to
keep business logic separated from view logic. Our advice is to break code in
small pieces and compose those pieces in simple and predictable ways.
Incidentally, this is a good advice for any piece of code ;).


Can it be used on Django? Flask? Etc?
=====================================

Of course! Hyperpython is completely framework agnostic. We have a few optional
integrations with Django, but it does not prevent Hyperpython of being used
in other frameworks or without any framework at all. It implements the __html__
interface which is recognized by most templating engines in Python. That way, it
is possible to pass Hyperpython fragments to existing templates in Django, Jinja2
and others.
