from abc import get_cache_token
from functools import wraps, partial
from types import MappingProxyType

from sidekick import import_later, deque

from .lazy_singledispatch import lazy_singledispatch

django_loader = import_later('django.template.loader')


def role_singledispatch(func):  # noqa: C901
    """
    Like single dispatch, but dispatch based on the type of the first argument
    and role string.
    """

    func_name = getattr(func, '__name__', 'callable')
    cls_wrapped = lazy_singledispatch(func)
    cls_register = cls_wrapped.register
    cls_dispatch = cls_wrapped.dispatch
    cls_registry = cls_wrapped.registry
    cache_token = None
    registry = {}
    dispatch_cache = {}

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
        try:
            cls_fallback = cls_registry[cls]
        except KeyError:
            cls_fallback = type_fallback(cls, func_name)
            cls_register(cls)(cls_fallback)

        def decorator(decorated):
            nonlocal cache_token

            cls_fallback.registry[role] = decorated
            registry[cls, role] = cls_fallback
            if cache_token is None and hasattr(cls, '__abstractmethods__'):
                cache_token = get_cache_token()
            dispatch_cache.clear()
            return decorated

        return decorator

    def dispatch(cls, role=None):
        """
        Return the implementation for the given type and role.

        If role is given, return a function that receives a single positional
        argument and any number of keyword arguments. If role is not given,
        the return function should receive both an object and a role as
        positional arguments.
        """
        nonlocal cache_token
        if cache_token is not None:
            current_token = get_cache_token()
            if cache_token != current_token:
                dispatch_cache.clear()
                cache_token = current_token

        try:
            return dispatch_cache[cls, role]
        except KeyError:
            cls_impl = cls_dispatch(cls)

            # We went all the way to the fallback function: there is no type
            # registered to handle the given request for any kind of role
            if cls_impl is func:
                if role is None:
                    impl = cls_impl
                else:
                    impl = partial(cls_impl, role=role)

            # Now we assume we have a function generated with the type_fallback
            # function. If role=None, we descent the mro() looking for a valid
            # implementation
            elif role is None:
                try:
                    impl = cls_impl.registry[None]
                except KeyError:
                    classes = deque(cls.mro())
                    classes.popleft()
                    for superclass in classes:
                        impl = dispatch(superclass)
                        if impl is not func:
                            break
                    else:
                        impl = func

            # Role is explicitly registered
            else:
                for superclass in cls.mro():
                    cls_impl = cls_dispatch(superclass)
                    if role in cls_impl.registry:
                        impl = cls_impl.registry[role]
                        break
                    elif None in cls_impl.registry:
                        impl = partial(cls_impl.registry[None], role=role)
                        break
                else:
                    impl = partial(func, role=role)

            # Save in cache and return
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


def type_fallback(cls, name):
    registry = {}

    def fallback(obj, role=None, **kwargs):
        try:
            func = registry[role]
        except KeyError:
            try:
                func = registry[None]
                kwargs['role'] = role
            except KeyError:
                raise error(obj.__class__, role)
        return func(obj, **kwargs)

    fallback.registry = registry
    fallback.type = cls
    if isinstance(cls, type):
        fallback.__name__ = f'{name}__{cls.__name__}'
        fallback.__qualname__ = fallback.__name__
    return fallback


def error(cls: type, role: str):
    assert isinstance(cls, type), f'bad argument: {cls}'
    tname = cls.__name__
    if role is None:
        return TypeError(f'no default role registered for {tname} objects')
    return TypeError(f'no "{role}" role registered for {tname} objects')
