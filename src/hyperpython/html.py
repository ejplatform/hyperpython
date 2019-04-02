from functools import wraps

from markupsafe import Markup
from sidekick import import_later, Proxy

from .core import Text, Element, Block, Blob
from .utils.role_dispatch import role_singledispatch, error

django_loader = import_later("django.template.loader")


def render(obj, role=None, **kwargs):
    """
    Like :func:`render`, but return a string of HTML code instead of a
    Hyperpython object.
    """
    return html(obj, role=role, **kwargs).__html__()


@role_singledispatch
def html(obj, role=None, **kwargs):
    """
    Convert object into a hyperpython structure.

    Args:
        obj:
            Input object.
        role:
            Optional description

        Additional context variables for the rendering process can be passed as
        keyword arguments.

    Returns:
        A hyperpython object.
    """
    # Try the html_role interface.
    try:
        method = obj.html_role
    except AttributeError:
        pass
    else:
        return method(role=role, **kwargs)

    # If role is given, we adopt a more strict behavior
    if role is not None:
        raise error(type(obj), role)

    # Fallback to __html__ or string renderers for role-less calls
    try:
        raw = obj.__html__()
    except AttributeError:
        return Text(str(obj))
    else:
        return Blob(raw)


#
# Auxiliary functions
#
def register_template(cls, template, role=None):
    """
    Decorator that registers a template-based renderer.

    (Currently, only Django is supported).

    Args:
        cls:
            Type of input object.
        template:
            Template name or list of template names.
        role:
            Optional role for the template.

    Examples:
        The decorated function must receive an instance of `cls` as first
        argument and any number of keyword arguments. It should return a context
        dictionary that is passed to the template to render the final HTML
        string.

        @render.register_template(User, 'users/user-contact.html', 'contact')
        def user_contact(user, **kwargs):
            return {
                'name': user.name,
                'email': user.get_public_email(),
                # ...
            }

        The role can be omitted to register a fallback implementation for the
        given model. The fallback receives the passed role as a keyword
        argument.

        @render.register_template(User, 'users/user-generic.html')
        def user_contact(user, role=None, **kwargs):
            return {
                'user': user,
                'role': role,
            }
    """
    template = django_loader.get_template(template)
    renderer = template.render

    def decorator(func):
        @html.register(cls, role)
        def wrapped(obj, **kwargs):
            ctx = func(obj, **kwargs)
            request = ctx.get("request")
            data = renderer(context=ctx, request=request)
            return Blob(data)

        return wrapped

    return decorator


html.register_template = register_template


#
# Register default renderers
#
def no_role(func):
    @wraps(func)
    def wrapped(x, role=None, **kwargs):
        if role is None:
            return func(x, **kwargs)
        raise error(type(x), role)

    return wrapped


html.register(Markup)(no_role(lambda x: Blob(x)))
html.register(str)(no_role(lambda x: Text(x)))
html.register(Proxy)(lambda x, **kwargs: html(x._obj__, **kwargs))

for _cls in (Element, Text, Block):
    html.register(_cls)(no_role(lambda x: x))
