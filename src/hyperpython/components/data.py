from collections.abc import Mapping, Iterable

from ..core import Element
from ..html import html
from ..tags import h
from ..tags import ul, ol, li, dl, dd, dt, table, thead, tbody, tr, td, th


@html.register(Iterable)
def html_list(data, role=None, ordered=False, **kwargs):
    """
    Convert a Python iterable into an HTML list element.

    Args:
        data:
            Sequence data.
        ordered:
            If True, returns an ordered list (<ol>) element.
        role:
            Role passed to render each item in the sequence.

        Additional keyword arguments are passed to the root element.

    Examples:
        >>> doc = html_list([1, 2, 3])
        >>> print(doc.pretty())
        <ul>
          <li>1</li>
          <li>2</li>
          <li>3</li>
        </ul>
    """
    tag = ol if ordered else ul
    body = [li(html(x, role=role)) for x in data]
    return tag(body, **kwargs)


@html.register(Mapping)
def html_map(data, role=None, key_role=None, **kwargs):
    """
    Renders mapping as a description list using dt as keys and dt as values.

    Args:
        data:
            Sequence data.
        role:
            Role passed to the dd (values) elements of the description list.
        key_role:
            Role passed to the dt (keys) elements of the description list.

        Additional keyword arguments are passed to the root element.

    Examples:
        >>> doc = html_map({'answer': 42, 'universe': True})
        >>> print(doc.pretty())
        <dl>
          <dt>answer</dt>
          <dd>42</dd>
          <dt>universe</dt>
          <dd>True</dd>
        </dl>
    """
    body = []
    items = getattr(data, "items", lambda: data)
    for k, v in items():
        body.append(dt(html(k, role=key_role)))
        body.append(dd(html(v, role=role)))
    return dl(body, **kwargs)


def html_table(data, *, role=None, columns=None, **kwargs):
    """
    Convert 2D matrix-like data to an HTML table.

    Args:
        data:
            Sequence data.
        role:
            Role used to render elements of the table.
        columns:
            A list of column names to be added as <thead>.

        Additional keyword arguments are passed to the root element.

    Examples:
        >>> doc = html_table([[1, 2], [3, 4]], columns=['a', 'b'])
        >>> print(doc.pretty())
        <table>
          <thead>
              <tr>
                <th>a</th>
                <th>b</th>
              </tr>
          </thead>
          <tbody>
              <tr>
                <td>1</td>
                <td>2</td>
              </tr>
              <tr>
                <td>3</td>
                <td>4</td>
              </tr>
          </tbody>
        </table>
    """
    options = {"role": role}
    body = [tr([td(html(obj, **options)) for obj in row]) for row in data]
    if columns is not None:
        head = tr([to_header_row(col, **options) for col in columns])
        return table([thead(head), tbody(body)], **kwargs)
    else:
        return table(body, **kwargs)


def to_header_row(obj, **options):
    data = html(obj, **options)
    return data if data.tag in ("td", "th") else th(data)


def wrap(obj, tag="div"):
    """
    Wraps object in a div (or any other specified tag) if it is not an element.
    """
    return obj if isinstance(obj, Element) else h(tag, {}, obj)
