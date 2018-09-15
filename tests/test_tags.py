import pytest

from hyperpython import a, div, p, title, head, Text, Json, h1, Block, h


# noinspection PyShadowingNames
class TestSimpleTagAttrsOperations:
    """
    Tests for a single tag object.
    """

    @pytest.fixture
    def a(self):
        return a(class_='cls1 cls2', id='id', href='url')['click me']

    def test_correct_tag_name(self, a):
        assert a.tag == 'a'

    def test_access_tag_attrs(self, a):
        assert a.attrs['id'] == 'id'
        assert a.attrs['class'] == ['cls1', 'cls2']
        assert a.attrs['href'] == 'url'

    def test_tag_id_attr(self, a):
        assert a.id == 'id'

    def test_tag_classes_attr(self, a):
        assert a.classes == ['cls1', 'cls2']

    def test_convert_tag_attrs_to_dict(self, a):
        assert a.attrs == {
            'class': ['cls1', 'cls2'], 'id': 'id', 'href': 'url'
        }

    def test_render(self, a):
        assert a.render() \
               == '<a class="cls1 cls2" id="id" href="url">click me</a>'

    def test_render_empty_class_list_as_empty(self):
        assert div(class_=()).render() == '<div></div>'

    def test_pretty(self):
        tag = div(class_='foo')[p('hello'), p('world')]
        html = (
            '<div class="foo">\n'
            '  <p>hello</p>\n'
            '  <p>world</p>\n'
            '</div>\n'
        )
        assert tag.pretty() == html

    def test_pretty_with_header_tags(self):
        assert head(title('title')).pretty(raw=True) == (
            '<head>\n'
            '  <title>title</title>\n'
            '</head>'
        )
        assert str(title('title').pretty()) == '<title>title</title>'


# noinspection PyShadowingNames
class TestCoreTagFunctionality:
    @pytest.fixture
    def a(self):
        return a(class_='cls', href='url')['click me']

    def test_tag_copy(self, a):
        assert str(a) == str(a.copy())
        assert a == a.copy()

    # noinspection PyProtectedMember
    def test_jupyter_repr(self):
        tag = p('foo')
        return tag._repr_html_() == tag.__html__()

    def test_can_set_tag_id(self):
        tag = p('foo')
        tag.id = 'bar'
        assert str(tag) == '<p id="bar">foo</p>'

    def test_getitem_creates_new_tag_with_extra_children(self, a):
        new = a['!']
        assert new is a
        assert str(new) == '<a class="cls" href="url">click me!</a>'

    # noinspection PyPropertyAccess
    def test_cannot_alter_id_of_non_tag_elements(self):
        x = Text('foo')
        with pytest.raises(AttributeError):
            x.id = 'bar'

    def test_can_walk(self):
        elem = div([h1('title'), p('title')])
        items = list(elem.walk())
        assert len(items) == 5

        elem = div([h1('title'), 'title'])
        assert len(list(elem.walk())) == 4

    def test_can_walk_in_tags(self):
        elem = div([h1('title'), p('title')])
        assert len(list(elem.walk_tags())) == 3

        elem = div([h1('title'), 'title'])
        assert len(list(elem.walk_tags())) == 2

    def test_can_append_element(self):
        tag = div('foo')
        tag.add_child('bar')
        assert str(tag) == '<div>foobar</div>'

    # noinspection PyPropertyAccess
    def test_block_api(self):
        children = [p('foo'), p('bar')]
        block = Block(children)
        assert list(block) == children
        assert len(block) == 2
        assert block[0] == children[0]
        assert str(block) == '<p>foo</p><p>bar</p>'
        assert block.id is None
        assert block.tag is None
        assert list(block.walk_tags()) == children

        with pytest.raises(AttributeError):
            block.id = 'foo'

    def test_text_api(self):
        obj = Text('foo')

        with pytest.raises(TypeError):
            obj.add_child(obj)

    def test_add_classes_fluid_api(self):
        tag = p('text')
        tag.add_class('foo').add_class('bar')

        # Add tag
        assert str(tag) == '<p class="foo bar">text</p>'

        # Add first
        tag.add_class('baz', first=True)
        assert str(tag) == '<p class="baz foo bar">text</p>'

        # Reset
        assert str(tag.set_class()) == '<p>text</p>'

    def test_cannot_create_children_in_void_elements(self):
        with pytest.raises(ValueError):
            print(h('br')['foo', 'bar'])

    def test_json_renders_correctly(self):
        obj = Json({'foo': 'bar'})
        assert str(obj) == '{"foo": "bar"}'
        assert obj.data == {'foo': 'bar'}
