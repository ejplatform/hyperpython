import re
from html import unescape
from random import choice
from string import ascii_letters, digits

from markupsafe import Markup, escape, escape_silent
from sidekick import import_later

# qa: used imports
bleach = import_later("bleach")
escape = escape
escape_silent = escape_silent
unescape = unescape
VALID_ID_CHARS = ascii_letters + digits + "_-"
STR_TYPES = (str, bytes, Markup)
SAFE_ATTRIBUTE_NAME = re.compile(r"^[^\s=<>&\"\']+$")


def dash_case(name):
    """
    Convert a camel case string to dash case.

    Example:
        >>> dash_case('SomeName')
        'some-name'
    """

    letters = []
    for c in name:
        if c.isupper() and letters and letters[-1] != "-":
            letters.append("-" + c.lower())
        else:
            letters.append(c.lower())
    return "".join(letters)


def snake_case(name):
    """
    Convert camel case to snake case.
    """

    return dash_case(name).replace("-", "_")


def random_id(prefix="id-", size=8):
    """
    Return a random valid HTML id.

    Args:
        prefix:
            A prefix string.
        size:
            The size of the random part of the string. The default value of 8
            gives a collision probability of ~ 3.5e-15, which is good enough for
            most cases.

    Returns:
        A random string.
    """
    if not prefix:
        prefix = choice(ascii_letters)
        size -= 1
    return prefix + "".join(choice(VALID_ID_CHARS) for _ in range(size))


def safe(x):
    """
    Convert string object to a safe Markup instance.
    """
    return Markup(x)


def sanitize(data, **kwargs):
    """
    Sanitize HTML and return as a safe string.
    """
    return safe(bleach.clean(data, **kwargs))


def html_natural_attr(x):
    """
    Convert string to a natural HTML attribute or tag name.

    This function replaces underscores by dashes.
    """
    return x.rstrip("_").replace("_", "-")


def html_safe_natural_attr(x):
    """
    Convert string to html natural name and check if the resulting string is
    valid.
    """
    return check_html_safe_name(html_natural_attr(x))


def check_html_safe_name(x):
    """
    Raises a ValueError if string is not a valid html attribute or tag name.
    """

    if not SAFE_ATTRIBUTE_NAME.match(x):
        raise ValueError("invalid html attribute name: %r" % x)
    return x
