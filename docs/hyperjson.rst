===============
HyperJSON (WIP)
===============

With the popularization of Virtual-DOM based Javascript frameworks, it has become
increasingly problematic to retrieve unstructured blobs of HTML that overrides
the innerHTML attribute of some element in the DOM. Hyperpython uses a specific
JSON serialization format to represent HTML data structures that can be used as
an alternative to transmit HTML from the back-end to the front-end. This plays
more nicely with technologies such as React, ELM or Vue.js. Moreover, it provides
the basis of a system to represent HTML templates in the client that not based
on string interpolation.

Tags as data structures
=======================

DOM means "Document Object Model". In informal parlance we use it to refer to
the "structure of our HTML document. In reality it describes much more: it
describes the API and the inheritance chain of how all HTML elements are described
in an object oriented fashion. We explicitly want to avoid that point of view and
focus solely on structure. Hyperpython is not concerned with the DOM, but rather
with the structure. The DOM is only relevant to the browser.

HyperJSON describes this nested HTML data structure using S-expressions. If you
are not familiar with S-expressions, it is a very nice idea popularized by LISP
to encode tree-like structures as nested lists. Our use-case is very simple,
since all tags become 3 element S-expressions:

    tag ==> [<tag-name>, <attributes>, <children>]

The first element is a string with the tag name, the second is an object mapping
attributes to their values and the third is a list of children nodes. Both the
second and the third arguments can be optionally omitted. The list of children is
formed by strings and other tag S-expressions.

An example is handy::

    <div class="foo">
        <h1>Title</h1>
        <p>Hello world!</p>
    </div>

Becomes::

    ["div", {"class": "foo"}, [
        ["h1", "Title"],
        ["p", "Hello World!"]
    ]

This is about the same size as the original HTML and represents the same data
structure.

Formalism
=========

This informal description is not good for language lawyers. Consider the elements
in http://json.org to specify HyperJSON with the BNF notation::

    element    : '[' name ',' attributes ','  children ']'
               | '[' name ',' attributes ']'
               | '[' name ',' children ']'

    name       : string

    attributes : object

    children   : '[' items ']'
               | string

    items      : item
               | item ',' items

    item       : string
               | tag


Semantics
---------

The attributes object does not support arbitrary values. Unless noted, all
attribute values must be strings. There are a few exceptions, though:

class:
    Class is a list of classes.


Converting from/to JSON
=======================

Hyperpython structures can be easily serialized as JSON or restored from HyperJSON
data. Use the :meth:`Element.to_json` method or the :func:`from_json` function
to convert from one format to the other.

Frontend integration
====================

There are only two options for now: a vanilla Javascript_ library that spits
DOM elements and an ELM_ library that produces nodes for ELM's virtual DOM.

.. _Javascript: http://github.com/fabiommendes/hyperjs/
.. _ELM: http://github.com/fabiommendes/hyperelm/


Extensions and templates
========================

We described the basic HyperJSON language. The client can optionally support
HyperJSON templates that makes easy to interpolate values for easy generation
of dynamic content on the client.
