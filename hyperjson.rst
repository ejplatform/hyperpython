=========
HyperJSON
=========

Intro
=====

HTML is a data serialization format for representing DOM trees. In a very
important sense, it is completely irrelevant. We obviously need a way to tell the
browser how it should construct the DOM. HTML is the status quo, but the
recent trend in frontend development seems to be avoiding HTML as much as
possible and generate bits of DOM tree using a combination of Javascript and
JSON. A lot of that is done through templating, i.e., bits of HTML source
are generated and then injected in specific places, however HTML markup can
(and maybe should) be completely avoided.

The DOM tree is a standard tree with meta-information (attributes and a tag
name) attached to element nodes. When seen as a serialization format for the DOM,
HTML has a lot of shortcomings:

* No typing information: everything, including attribute meta-information is 
  stringly typed.
* No notion of code reuse such as variables and functions.
* It is not the most human-friendly format.
* Robust HTML parsing (as implemented in most browsers and XML/HTML libraries) 
  is challenging.

The fact that modern web developers almost never create raw HTML files is
a hint to its inadequacies. What if we could ditch HTML and replace with
something else? Let us consider a few common patterns:

Templating
----------

There is
to create an alternative **syntax** (such as Pug, ex-Jade), but to define an
alternative data-structure that can be used to build


Alternative syntax
------------------


Javascript (or JSX)
-------------------


DOM as a data structure
-----------------------

Our proposition is to treat the DOM as a data structure and serialize it in 
JSON.


Basic representation
====================

The DOM has basically two kinds of nodes: elements (tags) and text fragments.
Consider the following fragment:

.. code-block:: html

    <div class="example">
        Hello <strong>World!</strong>
    </div>

HyperJSON uses a simple serialization scheme:

.. code-block:: json

    {
        "tag": "div",
        "attrs": {"class": ["example"]},
        "children": [
            {"text": "Hello "},
            {
                "tag": "strong",
                "children": [{"text": "World!"}]
            }
        ]
    }

It is obviously more verbose and less readable than HTML, but it is easier to
handle by machines. Humans should actually write in one of many alternative
syntaxes that compiles to HyperJSON. Of course is very easy to generate
proper HTML from an HyperJSON structure or to directly build a DOM tree in
the browser.


Templating
==========

Logic
=====

Logic nodes express 


::

    {"expr": "var", "name": <name>}

    {"expr": "let", "bind": {<name>: <value>}, "in": <expr>}

    {"expr": "if", "cond": <cond>, "then": <expr>, "else": <expr>}

    {"expr": "for", "var": <name>, "seq": <expr>, "block": <expr>}

    {"expr": "call", "function": <name>, "args": [<expr>]}


Variables
---------

::

    {"$var": <variable name>}

    {
        "$attrs": {},
    }

    {
        "$let": {
            <name 1>: <value 1>,
            <name 2>: <value 2>,
            ...
        },
        "$in": <expression>
    }

    {
        "$macro": <name>,
        "$inputs": {
            <name 1>: {"type": <type> [, "default": <value>]}

        },
        ""
    }


Extension nodes
===============

HyperJSON accepts many extension plugins to deliver different kinds of content.
Server-side implementations should support all those plugins and must be able
to create pure-HTML from them. Support in the browser is optional.

``{"markdown": <markdown source string>}``:
    Represents a paragraph in Markdown syntax. We recommend commonmark.

``{"latex": <latex equation (without dollar signs)>}``:
    A latex equation. Usually rendered with MathJax.

``{"latex-inline": <latex equation (without dollar signs)>}``:
    An inline LaTeX equation. Usually rendered with MathJax.

``{"": <>}``