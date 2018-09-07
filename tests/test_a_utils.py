from collections import OrderedDict

import pytest

from hyperpython.utils import lazy_singledispatch, html_safe_natural_attr, flatten


class TestLazySingleDispatch:
    def test_single_dispatch_example(self):
        @lazy_singledispatch
        def foo(x):
            return 42

        @foo.register(str)
        def _str(x):
            return x

        @foo.register('collections.OrderedDict')
        def _map(x):
            return dict(x)

        d = OrderedDict({3: 'three'})
        assert foo(1) == 42
        assert foo('two') == 'two'
        assert foo(d) == d


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


class TestSeqUtils:
    def test_flatten_lists(self):
        assert flatten([[1, 2], [3]]) == [1, 2, 3]
        assert flatten([1, [2, [3, 4]]]) == [1, 2, 3, 4]
