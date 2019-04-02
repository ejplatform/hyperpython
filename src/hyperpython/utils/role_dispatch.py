from abc import get_cache_token
from functools import wraps, partial

from sidekick import lazy_singledispatch
from types import MappingProxyType


def role_singledispatch(func):  # noqa: C901
    """
    Like single dispatch, but dispatch based on the type of the first argument
    and role string.
    """

    roles = {}
    no_roles = lazy_singledispatch(func)
    registry = {}
    dispatch_cache = {}
    cache_token = None

    def register(cls, role=None):
        """
        Register a renderer for a new type (possibly associated with an specific
        role)

        Args:
            cls (type):
                Type used to dispatch implementation.
            role (str):
                Roles define alternate contexts for rendering the same object.
        """
        if role is None:
            register_ = no_roles.register(cls)
        else:
            try:
                function = roles[role]
            except KeyError:

                def role_fallback(obj, **kwargs):
                    return no_roles(obj, role=role, **kwargs)

                function = roles[role] = lazy_singledispatch(role_fallback)
            register_ = function.register(cls)

        def decorator(func):
            dispatch_cache.clear()
            registry[cls, role] = func
            return register_(func)

        return decorator

    def dispatch(cls, role=None):
        """
        Return the implementation for the given type and role.

        If role is given, return a function that receives a single positional
        argument and any number of keyword arguments. If role is not given,
        the return function should receive both an object and a role as
        positional arguments.
        """
        # Invalidate cache when ABC cache is invalidated
        nonlocal cache_token
        if cache_token is not None and cache_token != get_cache_token():
            dispatch_cache.clear()
            cache_token = get_cache_token()

        try:
            return dispatch_cache[cls, role]
        except KeyError:
            pass

        # Find implementation, if not in cache
        if role is None:
            impl = no_roles.dispatch(cls)
        elif role in roles:
            impl = roles[role].dispatch(cls)
        else:
            impl = partial(no_roles.dispatch(cls), role=role)

        # Cache and return
        dispatch_cache[cls, role] = impl
        return impl

    @wraps(func)
    def wrapped(obj, role=None, **kwargs):
        impl = dispatch(obj.__class__, role)
        return impl(obj, **kwargs)

    wrapped.register = register
    wrapped.dispatch = dispatch
    wrapped.registry = MappingProxyType(registry)
    wrapped.clear_cache = dispatch_cache.clear
    return wrapped


def error(cls: type, role: str):
    assert isinstance(cls, type), f"bad argument: {cls}"
    tname = cls.__name__
    if role is None:
        return TypeError(f"no default role registered for {tname} objects")
    return TypeError(f'no "{role}" role registered for {tname} objects')
