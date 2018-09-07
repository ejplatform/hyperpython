====================
Django configuration
====================

Folks in Django like to add lines on the list of installed apps::

    # settings.py

    INSTALLED_APPS = [
        'hyperpython.django',
        ...
    ]

It works, but for now we do not do anything ;). In the future this line may
register new template tags and other integrations, but for now it is only possible
to avoid breaking expectations people have about "Django integration".

Template integration
====================

Hyperpython elements can be directly used in both Django and Jinja2 templates
without any additional configuration: just wrap them with `{{` and `}}`` and we
are good to go.


Going further
=============

Hyperpython can have also have a more important architectural role in a traditional
Django project with server side rendering. In Django, we are used to split our project
into pages with view functions mapping each "request" into the appropriate "response".
For complex layouts, this is often too much work in the hands of a single
function for it has to organize the rendering of lots of smaller pieces that
probably requires coordination of too many different responsibilities.

In practice, it is easy to fall into the anti-pattern of fat views + fat
templates. A common alternative to solve some of those problems is to move most
of the logic to the model, which creates a similarly bad problems with fat models
and does not touch the problem with the templates. (Some people advocate for
fat models since they provide better organization, testability and code reuse.
While this is probably true, it can also promote bad usage patterns of Django's
ORM since often some logic that now unnecessary lives on the model might
require inefficient instantiation of objects instead of direct manipulation of
querysets. In its worst incarnation, it might create a case of the very hard to
spot `n + 1 problem`_ in your codebase).

.. _n + 1 problem: https://github.com/jmcarp/nplusone

Hyperpython can help cutting cruft from the view functions by providing natural
ways of splitting them into smaller reusable pieces.


Hyperpython roles
-----------------

A Django view essentially maps an HTTP request (url + headers + some optional data)
to the corresponding response (data + headers), which is generally processed
by a templating engine. The view function is responsible for rendering a page.

Similarly, a Hyperpython role function receives an object and a role and return
an Hyperpython rendering of it. The point is to isolate functionality that can
be easily reused across different views. Even in cases where functionality is
used in a single page, it can be useful to reduce complexity by splitting
rendering in smaller and more focused parts.

Hyperpython stores a global mapping from objects and roles to their corresponding
renderers. This is declared using the ``register`` decorator method of
:func:`hyperpython.html` passing a type and a role:

.. code-block:: python

    from hyperpython import html, Text


    @html.register(int)
    def integer_fallback(x):
        """
        Fallback renderer for integers.
        """
        # This is not really necessary since the fallback renderer already
        # uses str() to create an HTML representation of an object.
        return Text(str(x))


    @html.register(int, 'currency')
    def dollars(x):
        """
        Represents a number as currency
        """
        return Text(f'U$ {x:.2f}')


    @html.register(int, 'roman')
    def transcribe(x):
        """
        Writes down the number as roman numeral.

        Works for numbers between 1 and 10.
        """
        numbers = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
        return Text(numbers[x - 1])


Now we can render integers using one of the specified roles:


>>> html(7, 'currency')
Text('U$ 7.00')

>>> html(7, 'roman')
Text('VII')

Role renderers can accept optional keyword arguments that may influence how
the final result is generated. A better implementation of currency, for instance,
could accept:

>>> html(7, 'currency', country='Brazil')                       # doctest: +SKIP
R$ 7,00

This is done by simply accepting additional keyword arguments in the function
definition.

Keep in mind that each renderer is associated to both a type and a role. The
functions above does not handle floats, for instance:

>>> html(7.0, 'currency')
Traceback (most recent call last):
...
TypeError: no "currency" role registered for float objects

Keeping that in mind, always consider using abstract types such as
:class:`types.Number` and :class:`collections.abc.Sequence`.


Roles in templates
------------------

Role renderers are globally available in Python code and can also be made
available inside templates. The exact configuration depends on your template
engine.

Jinja2
......

You must register the :func:`hyperpython.jinja2.filters.role` filter in your
Jinja2 environment. Now just use it to filter any variable::

    {{ user|role('contact-info-card', favorite=True) }}

This will be translated into ``html(user, 'contact-info-card', favorite=True)``.

Django
......

Not available yet, but PRs are welcome :)


Registered roles
----------------

Hyperpython has some builtin roles registered to common Python objects.

For now, the guideline is "read the code". (You can also contribute with
documentation).


Sequences and Querysets
-----------------------

:func:`html` uses a type/role based dispatch. This means that objects
that share the same type are not handled properly, which is precisely the case
of lists Django and querysets.

Generally speaking, queryset instances are all of the same type :class:`django.db.QuerySet`,
even for queries resulting from different models. Hence, queryset renderers are
not associated with models and cannot express useful constraints such
as a renderer for a "queryset of users".


Fragments
=========

:func:`html` solves the problem of "how render an object in some specific context".
Sometimes, we do not have an object that can be naturally associated with an HTML
fragment. For this, Hyperpython uses the :func:`fragment` function that instead
associates a string path to some HTML structure. This is very useful to declare
generic page elements such as headers, footers, etc:

.. code-block:: python

    from hyperpython import fragment, header, p

    @fragment.register('page.header')
    def render_header():
        return header('Minimalistic site header')

Now we render it using the :func:`fragment` function:

>>> fragment('page.header')
h('header', 'Minimalistic site header')

Those string paths can be parametrized and work very similarly to URLs in
frameworks like Django or Flask.

.. code-block:: python

    @fragment.register('count-<int:n>')
    def counter(n):
        # n is computed from the path given to the fragment function.
        return p(f'counting to {n}')


Fragments can be rendered using

>>> fragment('count-42')
h('p', 'counting to 42')

Beware to avoid pointless usage of path arguments (just like in the example
above).:func:`fragment` accepts optional keyword arguments that are passed
unchanged to the implementation and most of the time any extra parameter should
be treated as keyword arguments instead of a location on the path.

.. code-block:: python

    @fragment.register('count')
    def better_counter(n):
        return p(f'counting to {n}')


>>> fragment('count', n=42)
h('p', 'counting to 42')
