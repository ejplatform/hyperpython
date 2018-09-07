import pytest

from hyperpython import fragment, div, FragmentNotFound


@pytest.fixture(scope='session')
def fragments():
    @fragment.register('header')
    def f_header():
        return div('header')

    @fragment.register('footer')
    def f_footer():
        return div('footer')

    @fragment.register('user/<user>')
    def f_user(user):
        return div(f'user: {user}')

    @fragment.register('number/<int:number>')
    def f_number(number):
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

    def test_cannot_register_bad_path(self):
        with pytest.raises(ValueError):
            fragment.register('foo > bar')(lambda x: x)

    def test_validate_result_is_an_element(self):
        @fragment.register('bad')
        def foo():
            return 'foo'

        with pytest.raises(TypeError):
            print(fragment('bad'))

    def test_fragment_error(self):
        with pytest.raises(FragmentNotFound):
            fragment('not-found')
