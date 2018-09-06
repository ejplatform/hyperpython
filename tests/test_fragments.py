import pytest

from hyperpython import fragment, div


@pytest.fixture(scope='session')
def fragments():
    @fragment.register('header')
    def header():
        return div('header')

    @fragment.register('footer')
    def footer():
        return div('footer')

    @fragment.register('user/<user>')
    def user(user):
        return div(f'user: {user}')

    @fragment.register('number/<int:number>')
    def number(number):
        return div(f'number: {number + 1}')


class TestFragmentAPI:
    def test_simple_fragment(self, fragments):
        assert fragment('header') == div('header')
        assert fragment('footer') == div('footer')

    def test_fragment_with_string_path(self, fragments):
        assert fragment('user/foo') == div('user: foo')
        assert fragment('user/bar') == div('user: bar')

    def test_fragment_with_numeric_path(self, fragments):
        assert fragment('number/41') == div('number: 42')
        assert fragment('number/0') == div('number: 1')
