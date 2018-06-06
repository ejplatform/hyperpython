from sidekick import import_later
from .lazy_singledispatch import lazy_singledispatch

django_loader = import_later('django.template.loader')


def role_singledispatch(func):
    """
    Like single dispatch, but dispatch based on the type of the first argument
    and role string.
    """

    wrapped = lazy_singledispatch(func)
    single_register = wrapped.register
    single_dispatch = wrapped.dispatch

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
            impl = wrapped.registry[cls]
        except KeyError:
            impl = make_type_renderer(cls)
            single_register(cls)(impl)

        def decorator(func):
            impl.registry[role] = func
            return func

        return decorator

    def dispatch(cls, role=None):
        """
        Return the implementation for the given type and role.
        """

        impl = single_dispatch(cls)
        if role is None:
            return impl
        try:
            return impl.registry[role]
        except KeyError:
            try:
                return impl.registry[None]
            except KeyError:
                msg = 'no implementation for %s (role=%r' % (cls.__name__, role)
                raise TypeError(msg)

    wrapped.register = register
    wrapped.dispatch = dispatch
    return wrapped


def make_type_renderer(cls):
    registry = {}

    def render(obj, role=None, ctx=None):
        ctx = {} if ctx is None else ctx
        try:
            func = registry[role]
        except KeyError:
            try:
                func = registry[None]
            except KeyError:
                raise error(obj, role)
        return func(obj, ctx)

    render.registry = registry
    render.type = cls
    render.__name__ = f'render_{cls.__name__}'
    return render


def error(obj, role):
    tname = type(obj).__name__
    return TypeError('no method registered for %s (role=%r)' % (tname, role))
