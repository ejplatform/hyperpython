import pytest
import sidekick as sk
from mock import Mock

from hyperpython import Text, html, render, p
from hyperpython.components import (
    hyperlink, html_table, html_list, html_map, a_or_p,
    a_or_span, fa_icon, page
)
from hyperpython.components.hyperlinks import split_link
from hyperpython.core import as_child, Blob


class CustomType:
    def __str__(self):
        return 'custom'


class CustomTypeWithHtml:
    def __str__(self):
        return 'custom'

    def __html__(self):
        return '<div>custom</div>'


class CustomTypeWithHyperpython:
    def __hyperpython__(self):
        return '<div>custom</div>'


class TestRender:
    def test_render_base_python_types(self):
        assert render('hello') == 'hello'
        assert render(42) == '42'
        assert render(3.14) == '3.14'

    def test_escape_strings_when_rendering(self):
        assert render('<') == '&lt;'
        assert render([1, 2]) == '<ul><li>1</li><li>2</li></ul>'
        assert render({'foo': 'bar'}) == '<dl><dt>foo</dt><dd>bar</dd></dl>'

    def test_render_arbitrary_types(self):
        assert render(CustomType()) == 'custom'
        assert render(CustomTypeWithHtml()) == '<div>custom</div>'

    def test_dispatch_custom_type(self):
        class Type:
            pass

        @html.register(Type)
        def render_type(_, role=None):
            return Text('html' if role is None else f'html-{role}')

        assert render(Type()) == 'html'
        assert render(Type(), role='detail') == 'html-detail'

    def test_role_dispatch(self):
        assert html.dispatch(int)(42) == html(42)

        with pytest.raises(TypeError):
            print(html.dispatch(int, 'foo')(42))

    def test_conversion_to_children(self):
        assert as_child(42)
        assert as_child(p)
        assert as_child(CustomTypeWithHtml())
        assert as_child(CustomTypeWithHyperpython())

        with pytest.raises(TypeError):
            as_child({})


# noinspection PyShadowingNames
class TestDjangoRenderer:
    @pytest.yield_fixture
    def model_class(self):
        import sys

        class Base:
            pass

        class Model(Base):
            _meta = sk.record(app_label='app', model_name='model')

        sys.modules['django.db.models'] = sk.record(Model=Base)
        sys.modules['django.template.loader'] = sk.record(get_template=Mock())
        try:
            yield Model
        finally:
            del sys.modules['django.db.models']

    def test_render_django_model(self, model_class):
        @html.register_template(model_class, 'example.html', role='simple')
        def renderer(obj):
            return {'obj': obj, 'answer': 42}

        obj = model_class()
        result = html(obj, 'simple')
        assert isinstance(result, Blob)

    def test_cannot_render_wrong_role(self):
        with pytest.raises(TypeError):
            html('foo', 'bad-role')


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


class TestIcons:
    def test_render_font_awesome_icons(self):
        assert str(fa_icon('user')) == '<i class="fa fa-user"></i>'
        assert str(fa_icon('github')) == '<i class="fab fa-github"></i>'
        assert str(fa_icon('github', class_='cls')) == '<i class="fab fa-github cls"></i>'

    def test_render_icon_with_link(self):
        assert str(fa_icon('user', href='#')) == '<a href="#"><i class="fa fa-user"></i></a>'
        assert str(fa_icon('github', href='#')) == '<a href="#"><i class="fab fa-github"></i></a>'


class TestPageHead:
    def test_head_component(self):
        head = page.Head(
            title='My Page',
            favicons={
                57: '/icon-57.ico',
                128: '/icon-128.ico',
                'default': '/icon.ico',
            },
            google_analytics_id='g-id',
            meta_headers={'X-Frame-Options': 'sameorigin'}
        )
        head_html = str(head)
        assert '<title>My Page</title>' in head_html
        assert head_html.startswith('<head>')
        assert head_html.endswith('</head>')
