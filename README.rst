.. image:: https://readthedocs.org/projects/bricks/badge/?version=latest
    :target: http://bricks.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. image:: https://travis-ci.org/fabiommendes/django-bricks.svg?branch=master
    :target: https://travis-ci.org/fabiommendes/django-bricks
    :alt: Build status
.. image:: https://codeclimate.com/github/fabiommendes/django-bricks/badges/gpa.svg
    :target: https://codeclimate.com/github/fabiommendes/django-bricks
    :alt: Code Climate
.. image:: https://codecov.io/gh/fabiommendes/django-bricks/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/fabiommendes/django-bricks
    :alt: Code coverage
.. image:: https://www.quantifiedcode.com/api/v1/project/ee91ade50a344c87ac99638670c76580/badge.svg
    :target: https://www.quantifiedcode.com/app/project/ee91ade50a344c87ac99638670c76580
    :alt: Code issues


HyperPython
-----------

HyperPython is a Python interpretion of
`Hyperscript <http://https://github.com/hyperhype/hyperscript>`. This lib
allow us to generate, manipulate and query HTML documents using a small DSL
embedded in Python. Just like Hyperscript, the default entry
point is the `h` function:

>>> from hyperpython import h
>>> elem = h('p', {'class': 'hello'}, 'Hello World!')

This can be converted to HTML by calling ``str()`` on the element:

>>> print(str(elem))
<p class="hello">Hello World!</p>

Python and HTML have very different semantics. HTML's syntax gravitates
around tag attributes + children nodes and does not have a very natural
counterpart in most programming languages. It is obviously very easy to build
HTML tag in a imperative style, but the end result often feels awkward.
HyperPython embeds a simple DSL mini-language to declare HTML fragments in a
more natural way:

>>> from hyperpython import div, p, h1
>>> fragment = \
...     div(class_="alert-box")[
...         h1('Hello Python'),
...         p('Now you can write HTML in Python!'),
...     ]

By default, HyperPython stores the DOM node for a later use. We can introspect,
and modify the result.

>>> fragment.attrs['id'] = 'element-id'
>>> len(fragment.children)
2

We can use str() to print a very compact HTML or the ``.pretty()`` method to
get a more human-friendly version of the HTML.

>>> print(fragment.pretty())
<div class="alert-box" id="element-id">
  <h1>Hello Python</h1>
  <p>Now you can write HTML in Python!</p>
</div>