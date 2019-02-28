============
Skeleton.css
============

This module wraps `skeleton.css`_ in hyperpython. Milligram is a minimalistic
pure CSS framework that provides basic styles and under 2kb gzipped. It works
mostly by providing better default styles for HTML elements. On top of that,
it provides a few extra components and a simple grid system.

.. _skeleton.css: https://getskeleton.com
.. module:: hyperpython.contrib.milligram

Usage
=====

You can include the necessary imports in an hyperpython page by calling the
``milligram.cdn()`` function. This will add code to import all necessary assets
from a CDN:

.. code-block:: python

    # It acts as a drop-in replacement of hyperpython namespace.
    from hyperpython.contrib.milligram import *

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

.. automodule:: hyperpython.contrib.milligram
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

.. automodule:: hyperpython.contrib.milligram
    :members: container, row, column


