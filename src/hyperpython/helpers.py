from .utils.text import STR_TYPES


def classes(obj):
    """
    Return an iterator over the valid classes passed by object.
    """

    if obj is None:
        return
    elif isinstance(obj, STR_TYPES):
        yield from obj.split()
    elif isinstance(obj, dict):
        yield from (k for k, v in obj.items() if v is not False and v is not None)
    else:
        yield from obj
