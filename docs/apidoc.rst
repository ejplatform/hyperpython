.. module:: hyperpython

=============
API Reference
=============

API documentation for the Hyperpython module.


Basic types
-----------

.. autoclass:: Element
   :members:
   :inherited-members:

.. autoclass:: Text
   :members:

.. autoclass:: Block
   :members:

Functions
~~~~~~~~~

The generic entry point is the :func:`h` function. It also has functions with
same names of all HTML tags.

.. autofunction:: h


Creation of HTML elements for Python objects
--------------------------------------------

.. autofunction:: html
.. autofunction:: render
.. autofunction:: fragment


Hyperpython components
----------------------

.. module:: hyperpython.components

All functions bellow belongs to the :mod:`hyperpython.components` module.


Hyperlinks
~~~~~~~~~~

.. autofunction:: hyperlink
.. autofunction:: url
.. autofunction:: a_or_p
.. autofunction:: a_or_span
.. autofunction:: breadcrumbs


HTML data structures
~~~~~~~~~~~~~~~~~~~~

Those functions convert Python data structures to their natural HTML
representations.

.. autofunction:: html_list
.. autofunction:: html_map
.. autofunction:: html_table


Icons
~~~~~

Generic icon support using the <i> tag and helper functions for Font Awesome
icons.

.. autofunction:: icon
.. autofunction:: fa_icon
.. autofunction:: fab_icon


Text
~~~~

.. autofunction:: markdown