def flatten(seq, seqtypes=(list, tuple, set, type(_ for _ in []))):
    """
    Flatten a sequence of sequences.

    >>> flatten([1, [2, [3, 4]]])
    [1, 2, 3, 4]

    Returns:
        A flattened list.
    """

    result = []
    for elem in seq:
        if isinstance(elem, seqtypes):
            result.extend(flatten(elem, seqtypes))
        else:
            result.append(elem)
    return result
