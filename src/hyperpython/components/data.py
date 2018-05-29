from .core import render
from ..tags import ul, ol, li, dl, dd, dt, table, thead, tbody, tr, td


def html_list(data, ordered=False, role=None, strict=False, ctx=None, **kwargs):
    """
    Convert a Python iterable into an HTML list element.

    Args:
        data:
            Sequence data.
        ordered:
            If True, returns an ordered list (<ol>) element.
        role, strict, ctx:
            Arguments to pass to render() to transform each element in the
            sequence.

        Additional keyword arguments are passed to the root element.

    Examples:
        >>> doc = html_list([1, 2, 3])
        >>> pprint(doc)
        <ul>
            <li>1</li>
            <li>2</li>
            <li>3</li>
        </ul>'
    """
    tag = ol if ordered else ul
    body = [li(render(x, role=role, strict=strict, ctx=ctx)) for x in data]
    return tag(body, **kwargs)


def html_dict(data, role=None, ctx=None, strict=False, **kwargs):
    """
    Renders mapping as a description list.

    Args:
        data:
            Sequence data.
        role, strict, ctx:
            Arguments to pass to render() to transform each element in the
            sequence.

        Additional keyword arguments are passed to the root element.

    Examples:
        >>> doc = html_dict({'answer': 42, 'universe': True})
        >>> print(doc.pretty())
        <dl>
            <dt>answer</dt>
            <dd>42</dd>
            <dt>universe</dt>
            <dd>True</dd>
        </dl>
    """
    body = []
    for k, v in data.items():
        body.append(dt(render(k, role=role, ctx=ctx, strict=strict)))
        body.append(dd(render(v, role=role, ctx=ctx, strict=strict)))
    return dl(body, **kwargs)


def html_table(data, columns=None, role=None, ctx=None, strict=False, **kwargs):
    """
    Convert 2D matrix-like data to an HTML table.

    Args:
        data:
            Sequence data.
        columns:
            A list of column names to be added as <thead>.
        role, strict, ctx:
            Arguments to pass to render() to transform each element in the
            sequence.

        Additional keyword arguments are passed to the root element.

    Examples:
        >>> doc = html_table([[1, 2], [3, 4]], columns=['a', 'b'])
        >>> pprint(doc)
        <table>
            <thead>
                <tr><th>a</th><th>b</th>
            </thead>
            <tbody>
                <tr><td>1</td><td>2</td></tr>
                <tr><td>3</td><td>4</td></tr>
            </tbody>
        </table>
    """
    body = [
        tr([td(render(obj, role=role, strict=strict, ctx=ctx)) for obj in row])
        for row in data
    ]
    if columns:
        return table(**kwargs)[
            thead([render(col, role=role, strict=strict, ctx=ctx)
                   for col in columns]),
            tbody(body)
        ]
    else:
        return table(body, **kwargs)
