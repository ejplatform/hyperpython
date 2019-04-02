import functools
from abc import get_cache_token
from functools import update_wrapper
from types import MappingProxyType
from weakref import WeakKeyDictionary


def lazy_singledispatch(func):  # noqa: C901
    """
    Single-dispatch generic function decorator.

    Transforms a function into a generic function, which can have different
    behaviours depending upon the type of its first argument. The decorated
    function acts as the default implementation, and additional
    implementations can be registered using the register() attribute of the
    generic function.

    This implementation generalizes the default implementation in functools
    to accept lazy dispatch: implementations can be registered by class names
    instead of types. When it encounters an invalid argument, the multiple
    dispatch function will search if any class in this lazy registry is
    compatible with the given first argument type. It will automatically
    register this class and return the result.

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
                impl = find_implementation(cls, registry)
                if impl is func and lazy_registry:
                    for qualname in possible_qualnames(cls):
                        if qualname in lazy_registry:
                            impl = lazy_registry.pop(qualname)
                            register(cls)(impl)
                            break

            dispatch_cache[cls] = impl
        return impl

    def register(cls, impl=None):
        """generic_func.register(cls, impl) -> impl

        Registers a new implementation for the given *cls* on a *generic_func*.
        """
        nonlocal cache_token

        # First argument is a list of classes: iterate over all classes
        # registering one at a time.
        if not isinstance(cls, (type, str)):
            cls_list = list(cls)
            if impl is not None:
                for cls in cls_list:
                    register(cls, impl)
                return

        # Single class
        if impl is None:
            return lambda f: register(cls, f)
        if isinstance(cls, str):
            lazy_registry[cls] = impl
        else:
            registry[cls] = impl
        if cache_token is None and hasattr(cls, "__abstractmethods__"):
            cache_token = get_cache_token()
        dispatch_cache.clear()
        return impl

    def wrapper(*args, **kwargs):
        impl = dispatch(args[0].__class__)
        return impl(*args, **kwargs)

    registry[object] = func
    wrapper.register = register
    wrapper.dispatch = dispatch
    wrapper.registry = MappingProxyType(registry)
    wrapper.clear_cache = dispatch_cache.clear
    update_wrapper(wrapper, func)
    return wrapper


def possible_qualnames(cls):
    """
    Iterator over possible qualified names for class.
    """

    for subclass in cls.mro()[:-1]:
        path = subclass.__module__
        name = subclass.__qualname__

        while path:
            value = "%s.%s" % (path, name)
            yield value
            path, _, _ = path.rpartition(".")


find_implementation = getattr(functools, "_find_impl", None)
if find_implementation is None:
    raise RuntimeError("Could not import function _find_impl from functools")
