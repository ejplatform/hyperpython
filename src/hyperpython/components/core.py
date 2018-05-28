import functools

from sidekick import import_later
from ..core import Text

django_loader = import_later('django.template.loader')


@functools.singledispatch
def render(obj, role=None, ctx=None, strict=True):
    """
    Convert object into a hyperpython structure.

    Args:
        obj:
            Input object.
        role:
            Optional description
        ctx:
            Additional context variables for the rendering process.

    Returns:
        A hyperpython object.
    """
    if strict:
        raise render_error(obj, role)
    return Text(str(obj))


def register(cls, role=None):
    """
    Register a rendered for a new type (possibly associated with an specific
    role)

    Args:
        cls (type):
            Type used to dispatch implementation.
        role (str):
            Roles define alternate contexts for rendering the same object.
    """
    try:
        impl = render.registry[cls]
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
        msg = 'no implementation for %s (role=%r' % (cls.__name__, role)
        raise TypeError(msg)


def register_template(cls, template, role=None, object_variable=None):
    """
    Register a template-based renderer.

    (Currently, only Django templates are supported)

    Args:
        cls:
            Type of input object.
        template:
            Template name.
        role:
            Optional role for the template.
    """
    template = django_loader.get_template(template)
    renderer = template.render

    if isinstance(object_variable, str):
        object_variables = [object_variable]
    elif object_variable is None:
        object_variables = [cls.__name__.lower(), 'object']
    else:
        object_variables = list(object_variable)

    @register(cls, role=role)
    def template_function(obj, ctx=None):
        ctx = dict(ctx or {})
        ctx.update((name, obj) for name in object_variables)
        return Text(renderer(ctx), escape=False)

    return template_function


#
# Auxiliary functions
#
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
                raise render_error(obj, role)
        return func(obj, ctx)

    render.registry = registry
    render.type = cls
    render.__name__ = f'render_{cls.__name__}'
    return render


def render_fallback(obj, role=None, ctx=None):
    raise render_error(obj, role)


def render_error(obj, role):
    tname = type(obj).__name__
    return TypeError('no rendered registered for %s (role=%r)' % (tname, role))


#
# Register renderers
#
single_dispatch = render.dispatch
single_register = render.register
render.dispatch = dispatch
render.register = register
render.register_template = register_template


@render.register(str)
def _(data, ctx=None):
    return Text(data)


@render.register(int)
@render.register(float)
def _(data, ctx=None):
    return Text(str(data))
