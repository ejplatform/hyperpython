import pytest
from markupsafe import Markup

from hyperpython.components import markdown
from hyperpython.renderers import render_html, render_single_attr, render_attrs, \
    dump_html
from hyperpython.renderers.helpers import render_pretty
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


class TestRender:
    """
    Tests functions on bricks.helpers.render
    """

    def test_render_examples(self):
        assert render_html('bar') == 'bar'
        assert render_html(['foo', 'bar']) == 'foo bar'
        assert render_html(Markup('foo')) == 'foo'

    def test_render_renderable(self):
        class Foo:

            def __str__(self):
                return 'foo'

            __html__ = __str__

            def render(self):
                return str(self)

        foo = Foo()
        assert render_html(foo) == 'foo'

    def test_render_not_supported(self):
        with pytest.raises(TypeError):
            render_html(b'sdfsdf')

    def test_register_template(self):
        class Foo:
            __str__ = (lambda self: 'foo')

        handler = (lambda x: lambda ctx, f: f.write('{object}!'.format(**ctx)))
        dump_html.register_template(Foo, which=handler)
        assert Foo in dump_html.registry
        assert render_html(Foo()) == 'foo!'

    def test_register_template_using_decorator(self):
        class Foo:
            __str__ = (lambda self: 'foo')

        handler = (lambda x: lambda ctx, f: print(ctx) or f.write('{object}!'.format(**ctx)))

        @dump_html.register_context(Foo, which=handler)
        def get_context(x):
            return {'object': 42}

        assert Foo in dump_html.registry
        assert render_html(Foo()) == '42!'

    def test_pretty_printer(self):
        html = render_pretty('<div><p>foo</p></div>').strip()
        assert html == '<div>\n  <p>foo</p>\n</div>'
