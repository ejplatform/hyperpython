from sidekick import import_later
from ..core import Text, Element, Block
from ..utils.role_dispatch import role_singledispatch

django_loader = import_later('django.template.loader')


def render_html(obj, role=None, ctx=None, strict=True):
    """
    Like :func:`render`, but return a string of HTML code instead of a
    Hyperpython object.
    """
    return render(obj, role=role, ctx=ctx, strict=strict).__html__()


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
    try:
        return _render(obj, role, ctx)
    except TypeError:
        if strict:
            try:
                return Text(obj.__html__(), escape=False)
            except AttributeError:
                raise render_error(obj, role)
        return Text(str(obj))


def render_request(request, obj, role=None, ctx=None, strict=True):
    """
    Similar to render(), but receives a WSGI request as first argument.

    This function is framework agnostic, since WSGI is a Python protocol that is
    a protocol that is implemented by several frameworks. It is unlikely,
    however that implementations aimed to some specific framework will work
    correctly in other frameworks.
    """
    return _render_request(obj, role, request, ctx)


@role_singledispatch
def _render(obj, role, ctx=None):
    raise render_error(obj, role)


@role_singledispatch
def _render_request(obj, role, request=None, ctx=None):
    raise render(obj, role, ctx)


@_render.register(str)
def _render_str(data, ctx=None):
    return Text(data)


@_render.register(int)
@_render.register(float)
def _render_atom(data, ctx=None):
    return Text(str(data))


@_render.register(Element)
@_render.register(Text)
@_render.register(Block)
def _(obj, ctx=None):
    return obj


#
# Auxiliary functions
#
def render_fallback(obj, role=None, ctx=None):
    raise render_error(obj, role)


def render_error(obj, role):
    tname = type(obj).__name__
    return TypeError('no renderer registered for %s (role=%r)' % (tname, role))


def register_template(cls, template, role=None, object_variable=None):
    """
    Register a template-based renderer.

    (Currently, only Django templates are supported)

    Args:
        cls:
            Type of input object.
        template:
            Template name or list of template names.
        role:
            Optional role for the template.
        object_variable:
            A string or a list of strings with the name of the object variable
            passed to the template context.
    """
    template = django_loader.get_template(template)
    renderer = template.render

    if isinstance(object_variable, str):
        object_variables = [object_variable]
    elif object_variable is None:
        object_variables = [cls.__name__.lower(), 'object']
    else:
        object_variables = list(object_variable)

    @_render.register(cls, role=role)
    def template_renderer(obj, ctx=None):
        ctx = dict(ctx or {})
        ctx.update((name, obj) for name in object_variables)
        return Text(renderer(ctx), escape=False)

    return template_renderer


render.register = _render.register
render.dispatch = _render.dispatch
render.register_template = register_template


def register_request(cls):
    def decorator(func):
        def method(obj, role, request, **kwargs):
            return func(request, obj, role, **kwargs)

        method._function = func
        return _render_request.register(method)

    return decorator


def dispatch(cls, role=None):
    func = _render_request.dispatch(cls, role)
    try:
        return func._function
    except AttributeError:
        return lambda request, obj, role=None, **kwargs: func(obj, request, role, **kwargs)


render_request.register = register_request
render_request.dispatch = dispatch
