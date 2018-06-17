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
same names of HTML tags.

.. autofunction:: h



Components
----------

Basic interfaces
................

.. automodule:: hyperpython.components
   :members: render, render_html


Hyperlinks
..........

.. automodule:: hyperpython.components
   :members: hyperlink, url, a_or_p, a_or_span, breadcrumbs


HTML data structures
....................

Those functions convert Python data structures to their natural HTML
representations.

.. automodule:: hyperpython.components
   :members: html_list, html_map, html_table


Icons
.....

Generic icon support using the <i> tag and helper functions for Font Awesome
icons.

.. automodule:: hyperpython.components
   :members: icon, icon_link, fa_icon, fab_icon, fa_link, fab_link


Text
....

.. automodule:: hyperpython.components
   :members: markdown