def flatten(seq, seq_types=(list, tuple, set, type(_ for _ in []))):
    """
    Flatten a sequence of sequences.

    >>> flatten([1, [2, [3, 4]]])
    [1, 2, 3, 4]

    Returns:
        A flattened list.
    """

    result = []
    for elem in seq:
        if isinstance(elem, seq_types):
            result.extend(flatten(elem, seq_types))
        else:
            result.append(elem)
    return result
