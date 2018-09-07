import pytest

from hyperpython.components import markdown
from hyperpython.renderers import render_single_attr, render_attrs
from hyperpython.utils import sanitize, safe


class TestRenderAttrs:
    def test_attrs_examples(self):
        attrs = [('foo', 42), ('bar', 'bar')]
        assert render_attrs(attrs) == 'foo="42" bar="bar"'
        assert render_attrs(None, x=42) == 'x="42"'
        assert render_attrs({'foo': safe('bar')}) == 'foo="bar"'
        assert render_attrs({'foo': '<tag>'}) == 'foo="<tag>"'
        assert render_attrs({'foo': '"quote"'}) == 'foo="&quot;quote&quot;"'
        assert render_attrs({'foo': True, 'bar': False, 'baz': None}) == 'foo'

    def test_attrs_protocol(self):
        class Foo:
            attrs = [('x', 1), ('y', 2)]

        assert render_attrs(Foo()) == 'x="1" y="2"'

    def test_attrs_not_supported(self):
        class Foo:
            pass

        for x in [b'bytes', Foo()]:
            with pytest.raises(TypeError):
                print(render_single_attr(x))
            with pytest.raises(TypeError):
                print(render_attrs(x))

        with pytest.raises(TypeError):
            print(render_attrs('str'))

    def test_attr_examples(self):
        assert render_single_attr('foo') == 'foo'
        assert render_single_attr(
            {'foo': 'bar'}) == '{&quot;foo&quot;: &quot;bar&quot;}'


class TestEscape:
    """
    Tests functions on bricks.helpers.escape
    """

    def test_sanitize(self):
        assert sanitize('<b>foo</b>') == '<b>foo</b>'
        assert '<script>' not in sanitize('<script>foo</script')


class TestExtras:
    """
    Tests functions on bricks.helpers.extra
    """

    def test_markdown(self):
        assert markdown('#foo\n') == '<h1>foo</h1>'
