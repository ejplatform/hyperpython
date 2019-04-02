from functools import wraps


def extract_classes(flags):
    """
    Create a function that receives a dictionary of keyword arguments and
    extract classes from it.

    Function invocation changes the dictionary inplace.
    """
    flags = set(flags)

    def extractor(kwargs):
        if not kwargs:
            return ()

        common = flags.intersection(kwargs)
        if common:
            return [kwargs.pop(k) for k in common]
        else:
            return ()

    return extractor


def component(function=None, flags=(), prefix_classes=None, suffix_classes=None):
    """
    Basic component builder.
    """

    if function is None:
        return lambda func: component(func, flags, prefix_classes)

    extractor = extract_classes(flags)

    @wraps(function)
    def method(*args, **kwargs):
        classes = extractor(kwargs)
        elem = function(*args, **kwargs)
        if prefix_classes is not None:
            elem.add_class(prefix_classes, first=True)
        elem.add_class(classes)
        if suffix_classes is not None:
            elem.add_class(suffix_classes)
        return elem

    return method


def ui(elem):
    """
    Adds the ui class to the list of classes of element.
    """
    return elem.add_class("ui", first=True)


def ui_factory(func):
    """
    Return a function that adds the ui class to the list of classes of
    the element produced by ``func``.
    """
    return lambda *args, **kwargs: func(*args, **kwargs).add_class("ui", first=True)
