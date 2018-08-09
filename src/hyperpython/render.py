from sidekick import import_later, Proxy
from .core import Text, Element, Block
from .utils.role_dispatch import role_singledispatch

django_loader = import_later('django.template.loader')


def render_html(obj, role=None, **kwargs):
    """
    Like :func:`render`, but return a string of HTML code instead of a
    Hyperpython object.
    """
    return render(obj, role=role, **kwargs).__html__()


@role_singledispatch
def render(obj, role=None, **kwargs):
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
    try:
        raw = obj.__html__()
    except AttributeError:
        return Text(str(obj))
    else:
        return Text(raw, escape=False)


#
# Auxiliary functions
#
def register_template(cls, template, role=None, function=None):
    """
    Decorator that registers a template-based renderer.

    (Currently, only Django templates are supported).

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
    if function is not None:
        render.register_template(cls, template, role=role)(function)
        return

    template = django_loader.get_template(template)
    renderer = template.render

    def decorator(func):
        @render.register(cls, role)
        def wrapped(obj, **kwargs):
            ctx = func(obj, **kwargs)
            request = ctx.get('request')
            data = renderer(context=ctx, request=request)
            return Text(data, escape=False)

        return wrapped

    return decorator


render.register_template = register_template

#
# Register default renderers
#
render.register(str)(lambda x, **kwargs: Text(x))
render.register(Proxy)(lambda x, **kwargs: render(x._obj__, **kwargs))

for _cls in (Element, Text, Block):
    render.register(_cls)(lambda x, **kwargs: x)
