import pytest

from hyperpython import a, div


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


class TestCoreTagFunctionality:
    @pytest.fixture
    def a(self):
        return a(class_='cls', href='url')['click me']

    def test_tag_copy(self, a):
        assert str(a) == str(a.copy())
        assert a == a.copy()

    def test_getitem_creates_new_tag_with_extra_children(self, a):
        new = a['foo']
        assert new is not a
        assert str(new) == '<a class="cls" href="url">foo</a>'
