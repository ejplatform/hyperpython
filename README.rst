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


HyperPython
===========

HyperPython is a Python interpretion of
`Hyperscript <http://https://github.com/hyperhype/hyperscript>`_. If you are not
familiar with Hyperscript, think of it as React, but using pure Javascript
instead of JSX. Hyperpython allow us to generate, manipulate and query
HTML documents using a small DSL embedded in Python. And just like in Hyperscript,
the default entry point of Hyperpython the `h` function:

>>> from hyperpython import h
>>> elem = h('p', {'class': 'hello'}, 'Hello World!')

This can be converted to HTML by calling ``str()`` on the element:

>>> print(elem)
<p class="hello">Hello World!</p>

The p tag can also be created by the standalone p function (and we have a
corresponding function to each valid HTML5 tag).

>>> print(p({'class': 'hello'}, 'Hello World!'))
<p class="hello">Hello World!</p>

There is also no problem with nested structures:

>>> from hyperpython import div, p, h1
>>> fragment = \
...     div(class_="alert-box")[
...         h1('Hello Python'),
...         p('Now you can write HTML in Python!'),
...     ]

HyperPython returns a DOM-like structure which we can introspect, query and
modify later. The main usage, of course, is to generate strings of HTML source
code. We can apply the str() function for a compact representation of the output
code or call ``.pretty()`` method to to get a more human-friendly output.

>>> print(fragment.pretty())
<div class="alert-box" id="element-id">
  <h1>Hello Python</h1>
  <p>Now you can write HTML in Python!</p>
</div>
<BLANKLINE>


Secret goal: replace templating
===============================

The goal of ``hyperpython`` is to replace a lot of work that would be traditionally
done with a template engine such as Jinja2 by Python code that generates HTML
fragments. Templating languages are obviously more efficient than pure Python for
string interpolation, and should work fine for simple documents. For large systems,
however, templating can be tedious to create and very hard to maintain.
Templating is usually not a good answer to handle growing complexity.

Many recent Javascript libraries had played with direct manipulation of DOM or
virtual DOM nodes sidestepping the whole business of creating intermediate
HTML strings. React was probably the library that popularized this idea. As they
nicely put, "Templates separate technologies, not concerns". There is no point
on choosing a deliberately underpowered templating language that has poorly
communicates with your data sources and outputs your document in a flat string
representation since it does not improve architecture or organization.

The same lesson can be applied to Python on the server side. With Hyperpython,
we generate HTML directly in Python, instead of passing through an intermediate
templating step.

For those afraid of putting too much logic on templates, we recognize that
Hyperpython doesn't prevent anyone from shooting themselves on the foot, but neither
do any minimally powerful templating language. The discipline we must exercise
is to keep business logic separated from view logic (i.e., separate concerns).
Our advice is to break your code in small pieces and compose those pieces in
simple and predictable ways. Incidentally, this is a good advice for any piece
of code ;).


Can it be used on Django? Flask? Etc?
=====================================

Yes! Hyperpython is completely framework agnostic. We have a few optional
integrations with Django, but it does not prevent Hyperpython of being used
in other frameworks or without any framework at all. It implements the __html__
interface which is recognized by most templating engines in Python. That way, it
is possible to pass Hyperpython fragments to existing templates in Django, Jinja2
and others.
