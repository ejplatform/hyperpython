def flatten(seq, seqtypes=(list, tuple, set, type(_ for _ in []))):
    """
    Flatten a sequence of sequences.

    Returns:
        A flattened list.
    """

    result = []
    for elem in seq:
        if isinstance(elem, seqtypes):
            result.extend(elem)
        else:
            result.append(elem)
    return result
