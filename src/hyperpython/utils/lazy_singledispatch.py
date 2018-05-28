from abc import get_cache_token
from functools import _find_impl, update_wrapper
from types import MappingProxyType
from weakref import WeakKeyDictionary


# TODO(?): maybe we should not use undocumented APIs ;)


def _possible_qualnames(cls):
    """
    Iterator over possible qualified names for class.
    """

    for subclass in cls.mro()[:-1]:
        path = subclass.__module__
        name = subclass.__qualname__

        while path:
            value = '%s.%s' % (path, name)
            yield value
            path, _, _ = path.rpartition('.')


def lazy_singledispatch(func):
    """
    Single-dispatch generic function decorator.

    Transforms a function into a generic function, which can have different
    behaviours depending upon the type of its first argument. The decorated
    function acts as the default implementation, and additional
    implementations can be registered using the registerPlugin() attribute of the
    generic function.

    This implementation generalizes the default implementation in functools
    to accept lazy dispatch: implementations can be registered by class names
    instead of types. When it encounters an invalid argument, the multiple
    dispatch function will search if any class in this lazy registry is
    compatible with the given first argument type. It will automatically
    registerPlugin this class and return the result.

    Usage:

        @lazy_singledispatch
        def func(x):
            return abs(x)

        @func.register(complex)
        def _(z):
            return abs(z.real) + abs(z.image)

        @func.register('numpy.ndarray')
        def _(seq):
            return sum(abs(x) for x in seq)

    Now this function can be used with any python object and will dispatch
    to the most specialized implementation. A important aspect of lazy dispatch
    is that a deferred class such as ``'numpy.ndarray'`` doesn't need to be
    loaded at registry time. This avoids potentially expensive imports (e.g.,
    numpy, django or pandas) and can be used to implement handlers for optional
    dependencies.

    Unfortunately, this mechanism **does not** work with abstract classes. The
    given name must match a concrete name of an argument type or any of its
    parents.

    So if you register a lazy dispatch to 'collections.Sequence', it will match
    any object that is a direct descendant of 'collections.Sequence',
    but it will not match a list, even though ``isinstance([...], collections.Sequence)``
    is True.
    """
    registry = {}
    lazy_registry = {}
    dispatch_cache = WeakKeyDictionary()
    cache_token = None

    def fallback(x, *args, **kwargs):
        """
        Call generic function x with argument of type registered with the
        lazy_register decorator.

        This will search the function cache for a suitable implementation and
        registerPlugin it when with the generic function when it is found.
        """

        cls = x.__class__
        if lazy_registry:
            for qualname in _possible_qualnames(cls):
                if qualname in lazy_registry:
                    implementation = lazy_registry.pop(qualname)
                    wrapper.register(cls, implementation)
                    return wrapper(x, **kwargs)
        dispatch_cache[cls] = func
        return func(x, *args, **kwargs)

    def dispatch(cls):
        """generic_func.dispatch(cls) -> <function implementation>

        Runs the dispatch algorithm to return the best available implementation
        for the given *cls* registered on *generic_func*.

        """
        nonlocal cache_token
        if cache_token is not None:
            current_token = get_cache_token()
            if cache_token != current_token:
                dispatch_cache.clear()
                cache_token = current_token
        try:
            impl = dispatch_cache[cls]
        except KeyError:
            try:
                impl = registry[cls]
            except KeyError:
                impl = _find_impl(cls, registry)
            dispatch_cache[cls] = impl
        return impl

    def register(cls, func=None):
        """generic_func.registerPlugin(cls, func) -> func

        Registers a new implementation for the given *cls* on a *generic_func*.

        """
        nonlocal cache_token

        # First argument is a list of classes: iterate over all classes
        # registering one at a time.
        if not isinstance(cls, (type, str)):
            cls_list = list(cls)
            if func is not None:
                for cls in cls_list:
                    register(cls, func)
                return
            # else:
            #     def decorator(func):
            #         for cls in cls_list:
            #             registerPlugin(cls, func)
            #     return decorator

        # Single class
        if func is None:
            return lambda f: register(cls, f)
        if isinstance(cls, str):
            lazy_registry[cls] = func
        else:
            registry[cls] = func
        if cache_token is None and hasattr(cls, '__abstractmethods__'):
            cache_token = get_cache_token()
        dispatch_cache.clear()
        return func

    def wrapper(*args, **kw):
        return dispatch(args[0].__class__)(*args, **kw)

    registry[object] = fallback
    wrapper.register = register
    wrapper.dispatch = dispatch
    wrapper.registry = MappingProxyType(registry)
    wrapper._clear_cache = dispatch_cache.clear
    update_wrapper(wrapper, func)
    return wrapper
