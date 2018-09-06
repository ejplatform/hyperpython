from functools import partial
from types import MappingProxyType

from sidekick import import_later

from .lazy_singledispatch import lazy_singledispatch

django_loader = import_later('django.template.loader')


def role_singledispatch(func):  # noqa: C901
    """
    Like single dispatch, but dispatch based on the type of the first argument
    and role string.
    """

    wrapped = lazy_singledispatch(func)
    cls_register = wrapped.register
    cls_dispatch = wrapped.dispatch
    cls_registry = wrapped.registry
    registry = {}

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
            impl = cls_registry[cls]
        except KeyError:
            impl = make_type_renderer(cls)
            cls_register(cls)(impl)

        def decorator(decorated):
            impl.registry[role] = decorated
            registry[cls, role] = impl
            return decorated

        return decorator

    def dispatch(cls, role=None):
        """
        Return the implementation for the given type and role.
        """
        impl = cls_dispatch(cls)
        if role is None:
            return impl
        try:
            return impl.registry[role]
        except KeyError:
            return partial(impl, role=role)

    wrapped.register = register
    wrapped.dispatch = dispatch
    wrapped.registry = MappingProxyType(registry)
    return wrapped


def make_type_renderer(cls):
    registry = {}

    def render(obj, role=None, **kwargs):
        try:
            func = registry[role]
        except KeyError:
            try:
                func = registry[None]
                kwargs['role'] = role
            except KeyError:
                raise error(obj, role)
        return func(obj, **kwargs)

    render.registry = registry
    render.type = cls
    if isinstance(cls, type):
        render.__name__ = f'render_{cls.__name__}'
    return render


def error(obj, role):
    tname = type(obj).__name__
    return TypeError(f'no "{role}" role for {tname} objects')
