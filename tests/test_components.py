import pytest

from hyperpython import Text
from hyperpython.components import hyperlink, render_html, render, html_table, html_list, html_map
from hyperpython.components.hyperlinks import split_link, a_or_p, a_or_span


class CustomType:
    def __str__(self):
        return 'custom'


class TestRender:
    def test_render_base_python_types(self):
        assert render_html('hello') == 'hello'
        assert render_html(42) == '42'
        assert render_html(3.14) == '3.14'

    def test_escape_strings_when_rendering(self):
        assert render_html('<') == '&lt;'
        assert render_html([1, 2]) == '<ul><li>1</li><li>2</li></ul>'
        assert render_html({'foo': 'bar'}) == '<dl><dt>foo</dt><dd>bar</dd></dl>'

    def test_render_arbitrary_types_in_non_strict_mode(self):
        assert render_html(CustomType(), strict=False) == 'custom'

    def test_fail_in_strict_mode(self):
        with pytest.raises(TypeError):
            render_html(CustomType())

    def test_dispatch_custom_type(self):
        class Type:
            pass

        @render.register(Type)
        def render_type(x, ctx=None):
            return Text('html')

        assert render_html(Type(), role='detail') == 'html'
        assert render.dispatch(Type)(Type()) == 'html'
        assert render.dispatch(Type, role='detail')(Type()) == 'html'


class TestHyperlink:
    """
    Tests functions on bricks.helpers.hyperlink
    """

    def test_hyperlink_examples(self):
        link = '<a href="bar">foo</a>'
        assert hyperlink('foo<#>').render() == '<a href="#">foo</a>'
        assert hyperlink('foo', 'bar').render() == link
        assert hyperlink({'href': 'bar', 'content': 'foo'}).render() == link
        assert hyperlink('foo', **{'href': 'bar'}).render() == link

    def test_hyperlink_not_supported(self):
        with pytest.raises(TypeError):
            hyperlink(hyperlink)

    def test_parse_link_function(self):
        assert split_link('foo') == ('foo', None)
        assert split_link('foo<bar>') == ('foo', 'bar')
        assert split_link('foo <bar>') == ('foo', 'bar')

    def test_conditional_anchors(self):
        assert a_or_p('click').__html__() == '<p>click</p>'
        assert a_or_p('click', href='#').__html__() == '<a href="#">click</a>'
        assert a_or_span('click').__html__() == '<span>click</span>'
        assert a_or_span('click', href='#').__html__() == '<a href="#">click</a>'


class TestDataRenderers:
    def test_render_html_table(self):
        assert (html_table([[1, 2]]).__html__()
                == '<table><tr><td>1</td><td>2</td></tr></table>')
        assert (html_table([[1, 2]], columns=['a', 'b']).__html__()
                == '<table><thead><tr><th>a</th><th>b</th></tr></thead>'
                   '<tbody><tr><td>1</td><td>2</td></tr></tbody></table>')

    def test_render_html_list(self):
        assert (html_list([1, 2]).__html__()
                == '<ul><li>1</li><li>2</li></ul>')
        assert (html_list([1, 2], ordered=True).__html__()
                == '<ol><li>1</li><li>2</li></ol>')

    def test_render_html_map(self):
        assert (html_map({'foo': 'bar'}, class_='foo').__html__()
                == '<dl class="foo"><dt>foo</dt><dd>bar</dd></dl>')