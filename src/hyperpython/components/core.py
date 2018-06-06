from sidekick import import_later
from ..core import Text
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


@role_singledispatch
def _render(obj, role, ctx):
    raise render_error(obj, role)


@_render.register(str)
def _render_str(data, ctx=None):
    return Text(data)


@_render.register(int)
@_render.register(float)
def _render_atom(data, ctx=None):
    return Text(str(data))


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
