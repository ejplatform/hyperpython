from collections import OrderedDict

import pytest
from hyperpython.utils import flatten
from hyperpython.utils import  html_safe_natural_attr
from hyperpython.utils.role_dispatch import role_singledispatch
from hyperpython.utils.text import snake_case, dash_case, random_id





class TestRoleDispatch:
    def test_can_dispatch_to_generic_super_type(self):
        class Foo:
            __str__ = (lambda x: 'foo')

        class Bar(Foo):
            __str__ = (lambda x: 'bar')

        @role_singledispatch
        def func(x, role):
            return f'{x} - {role}'

        @func.register(Bar, 'upper')
        def bar_upper(x):
            return str(x).upper()

        @func.register(Foo)
        def foo(x):
            return str(x)

        assert func(Bar(), 'upper') == 'BAR'
        assert func(Foo()) == 'foo'
        assert func(Bar()) == 'bar'

    def test_can_register_role_to_object(self):
        @role_singledispatch
        def func(x, role=None):
            return f'{x}:{role}'

        @func.register(object, 'uppercase')
        def _(x):
            return str(x).upper()

        assert func('foo', role='bar') == 'foo:bar'
        assert func('foo', role='uppercase') == 'FOO'


class TestStringUtils:
    def test_attr_names(self):
        assert html_safe_natural_attr('data-foo') == 'data-foo'
        assert html_safe_natural_attr('data_foo') == 'data-foo'
        assert html_safe_natural_attr('v-bind:foo') == 'v-bind:foo'
        assert html_safe_natural_attr(':foo') == ':foo'
        assert html_safe_natural_attr('@foo') == '@foo'

    def test_html_natural_attr_does_not_accept_invalid_attrs(self):
        invalid = ['foo bar', 'foo"', 'foo=', 'foo\'']
        for name in invalid:
            with pytest.raises(ValueError):
                html_safe_natural_attr(name)

    def test_case_transformers(self):
        assert snake_case('FooBar') == 'foo_bar'
        assert dash_case('FooBar') == 'foo-bar'

    def test_random_id(self):
        assert random_id(prefix='foo-').startswith('foo-')
        assert random_id().startswith('id-')
        r_id = random_id(prefix=None, size=10)
        assert len(r_id) == 10
        assert r_id[0].isalpha()


class TestSeqUtils:
    def test_flatten_lists(self):
        assert flatten([[1, 2], [3]]) == [1, 2, 3]
        assert flatten([1, [2, [3, 4]]]) == [1, 2, 3, 4]
