import re
from collections import OrderedDict

from .core import BaseElement

identity = lambda x: x
FRAGMENT_REGISTRY = OrderedDict()
SIMPLE_PATH_REGISTRY = {}
PATH_REGEX = re.compile(r"<[a-zA-Z]\w*(?::[a-zA-Z]\w*)?>")
KIND_REGEX_MAP = {
    "str": r".+",
    "int": r"\d+",
    "float": r"\d+(\.\d+)?",
    "slug": r"[\w-]+",
}
KIND_COERCION_MAP = {"str": identity, "int": int, "float": float, "slug": identity}


def fragment(path, **kwargs):
    """
    Compute the Hyperpython element for the given fragment path.

    Args:
        path (str):
            Argument path.

    Examples:
        >>> fragment('page.header', user='me!')                  # doctest: +SKIP
        h('header', ['Hello me!'])
    """
    try:
        func = SIMPLE_PATH_REGISTRY[path]
    except KeyError:
        for key, func in FRAGMENT_REGISTRY.items():
            args = key(path)
            if args is not None:
                try:
                    result = func(**args, **kwargs)
                except FragmentNotFound:
                    continue
                else:
                    break
        else:
            raise FragmentNotFound(f"no fragment registered to {path}")
    else:
        result = func(**kwargs)

    if not isinstance(result, BaseElement):
        cls = type(result).__name__
        msg = f"fragment function returned {cls} instead of element"
        raise TypeError(msg)
    return result


def register(path):
    """
    Register render function to the given fragment path spec.

    Args:
        path (str):
            A path spec.
    """

    def decorator(func):
        if "<" in path or ">" in path:
            FRAGMENT_REGISTRY[make_validator(path)] = func
        else:
            SIMPLE_PATH_REGISTRY[path] = func
        return func

    return decorator


def make_validator(spec):
    """
    Return a validator function from the given spec.

    The validator function returns None if the path does not correspond to the
    spec or a dictionary of arguments otherwise.

    Args:
        spec:
            A path spec using Django-like path specification.
    """
    regex, coercion = make_regex(spec)

    def validator(path):
        m = regex.match(path)
        if m is not None:
            return coercion(m.groupdict())
        else:
            return None

    return validator


def make_regex(spec):
    """
    Convert a path spec to a regular expression + map of coercion functions.

    Args:
        spec (str):
            A valid path spec in the form of "foo.<bar>.<int:baz>".

    Returns:
        A tuple of (compiled regex, coercion function).
    """

    data = spec
    parts = ["^"]
    coercions = {}
    search = PATH_REGEX.search
    variables = set()

    m = search(data)
    while m:
        i, j = m.span()
        start, sep, data = data[:i], data[i:j], data[j:]
        pattern = sep[1:-1]
        if ":" in pattern:
            kind, name = pattern.split(":")
        else:
            kind = "str"
            name = pattern

        # Prevent repeated variables in the spec
        if name in variables:
            raise ValueError(f"{name} is used twice in path spec")
        variables.add(name)

        # Prevent malformed paths
        validate_simple_path(start, spec)

        # Create fragment path and coercion function
        arg_regex = rf"(?P<{name}>{argument_regex(kind)})"
        coercions[name] = argument_coercion(kind)

        parts.append(re.escape(start))
        parts.append(arg_regex)

        m = search(data)

    validate_simple_path(data, spec)
    parts.append(re.escape(data))
    parts.append("$")

    return re.compile("".join(parts)), coercion_function(coercions)


fragment.register = register


def argument_regex(kind):
    """
    Return a regex corresponding to the given path type (e.g., str, int, float,
    etc)

    Args:
        kind (str):
            One of 'str', 'int', 'float', 'slug'

    Returns:
        A regex string.
    """
    try:
        return KIND_REGEX_MAP[kind]
    except KeyError:
        raise ValueError(f"invalid path type: {kind}")


def argument_coercion(kind):
    """
    Return a function that transform a string corresponding to the path fragment
    to the proper Python type (e.g., str, int, float, etc)

    Args:
        kind (str):
            One of 'str', 'int', 'float', 'slug'

    Returns:
        A coercion function.
    """
    try:
        return KIND_COERCION_MAP[kind]
    except KeyError:
        raise ValueError(f"invalid path type: {kind}")


def coercion_function(coercions):
    """
    Return a coercion function from a mapping of coercions.

    The coercion function converts a map to strings to a map to the correct
    types.
    """

    def coercion(dic):
        return {k: coercions.get(k, identity)(v) for k, v in dic.items()}

    return coercion


def validate_simple_path(st, path):
    """
    Prevent incomplete path specifications.
    """
    if "<" in st or ">" in st:
        raise ValueError(f"invalid path spec: {path}")


#
# Exceptions
#
class FragmentNotFound(Exception):
    """
    Raised for non-registered fragments.
    """
