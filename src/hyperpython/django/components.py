from django.middleware.csrf import get_token

from .. import input_


def csrf_input(request=None, token=None, name="csrfmiddlewaretoken", **kwargs):
    """
    Return an <input> field with the CSRF token.

    Normally, request should be given as first argument. If not given, one must
    provide a token value to be passed to the input element.

    >>> print(csrf_input(request))
    <input type="hidden" name="csrfmiddlewaretoken" value="csrf-token-value"></input>
    """

    if request is None and token is not None:
        token = token
    elif request is not None:
        token = get_token(request)
    else:
        raise TypeError("cannot retrieve CSRF token from empty request.")
    return input_(type="hidden", name=name, value=token, **kwargs)
