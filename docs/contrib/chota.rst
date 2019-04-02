=========
Chota.css
=========

TODO

This module wraps `chota.css`_ in hyperpython. Chota is a minimalistic
pure CSS framework that provides basic styles and uses CSS variables for
customization. It is under 3kb gzipped and provides a grid system and some
basic components.

.. _chota.css: https://chota.com
.. module:: hyperpython.contrib.chota

.. admonition:: warning

    THIS IS A WORK IN PROGRESS

    I kept this file here since contributing support for a new framework,
    specially one of those minimalistic ones such as Chota, is a great way
    to start contributing.


Usage
=====

You can include the necessary imports in an hyperpython page by calling the
``chota.cdn()`` function. This will add code to import all necessary assets
from a CDN:

.. code-block:: python

    # It acts as a drop-in replacement of hyperpython namespace.
    from hyperpython.contrib.chota import *

    page = \
        document([
            head([
                title('My page'),
                cdn(),
            ]),
            body([
                h1('Hello Milligram'),
                button('Click me!'),
            ]),
        ])



Components
==========

.. automodule:: hyperpython.contrib.chota
    :members: button, label


Grid system
===========

In order to use the grid system, adds row elements inside a :func:`container`
and :func:`column` children inside each :func:`row`:


.. code-block:: python

    page = container(
        row(
            column('col-a1', size=33, align='top'),
            column('col-b1', size=66),
        ),
        row(
            column('col-b2', size=33, offset=33),
        ),
    )

.. automodule:: hyperpython.contrib.chota
    :members: container, row, column


