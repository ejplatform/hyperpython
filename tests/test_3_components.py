import pytest

from hyperpython.components import hyperlink
from hyperpython.components.hyperlinks import parse_link


class TestHyperlink:
    """
    Tests functions on bricks.helpers.hyperlink
    """

    def test_hyperlink_examples(self):
        link = '<a href="bar">foo</a>'
        assert hyperlink('foo').render() == '<a>foo</a>'
        assert hyperlink('foo', 'bar').render() == link
        assert hyperlink({'href': 'bar', 'content': 'foo'}).render() == link
        assert hyperlink('foo', **{'href': 'bar'}).render() == link

    def test_hyperlink_not_supported(self):
        with pytest.raises(TypeError):
            hyperlink(b'sdfsdf')

    def test_parse_link_function(self):
        assert parse_link('foo') == ('foo', None)
        assert parse_link('foo<bar>') == ('foo', 'bar')
        assert parse_link('foo <bar>') == ('foo', 'bar')
