import collections
import io

from sidekick import import_later
from ..utils import lazy_singledispatch, escape, snake_case

jinja2 = import_later('jinja2')
django_template = import_later('django.template.loader:select_template')


@lazy_singledispatch
def dump_html(obj, file):
    """
    Dump object as a safe HTML string into file.

    This function uses single dispatch to make it extensible for user defined
    types::

        @dump_html.register(int)
        def _(x, file):
            if x == 42:
                return file.write('the answer')
            else:
                return file.write(str(x))

    A very common pattern is to render object from a template. This has
    specific support::

        dump_html.register_template(UserProfile, 'myapp/user_profile.jinja2')

    By default, it populates the context dictionary with a snake_case version
    of the class name, in this case, ``{'user_profile': x}``. The user may pass
    a ``context`` keyword argument to include additional context data.

    If you want to personalize how this is done, it is possible to use
    register_template to register a context factory function. The function
    should receive the object, a request and kwargs::

        @dump_html.register_template(UserProfile, 'myapp/user_profile.jinja2')
        def context(profile, request=None, context=None, **kwargs):
            context = context or {}
            context.update(kwargs, request=request, profile=profile)
            return context
    """
    # Tries the object .__html__ method
    if hasattr(obj, '__html__'):
        return file.write(obj.__html__())

    raise TypeError('type not supported: %r' % obj.__class__.__name__)


def render_html(obj):
    """
    Similar to dump_html, but return a string instead of writing to a file.
    """

    # Tries the object .__html__ method
    if hasattr(obj, '__html__'):
        return obj.__html__()
    file = io.StringIO()
    dump_html(obj, file)
    return file.getvalue()


#
# Register custom handlers for the dump function.
#
@dump_html.register(str)
def _html_str(x, file):
    return file.write(escape(x))


@dump_html.register(collections.Sequence)
def _html_sequence(seq, file):
    write = file.write
    iterator = iter(seq)
    pos = file.tell()
    try:
        dump_html(next(iterator), file)
    except StopIteration:
        pass
    for x in iterator:
        new_pos = file.tell()
        if new_pos != pos:
            write(' ')
        else:
            pos = new_pos
        dump_html(x, file)


@dump_html.register('django.db.models.Model')
def _html_django_model(obj, file):
    cls = obj.__class__
    template_name = '%s/%s' % (cls._meta.app_label, cls._meta.model_name)
    template_name = [template_name + '.html', template_name + '.jinja2']
    register_template(cls, template_name=template_name)
    implementation = dump_html.registry[type(obj)]
    return implementation(obj, file)


#
# HTML Templates
#
def register_template(cls, template_name=None, object_context_name=None,
                      get_context=None, which=None):
    """
    Register the default template name for the given type.

    Args:
        cls:
            A type for single dispatch.
        template_name (str, list):
            The template name. If no template is given, it automatically selects
            '<base module>/<class name>.<ext>'.
        object_context_name (str):
            Name of the variable that holds the object in the context
            dictionary.
        get_context:
            A function with signature f(obj) that generates the context
            dictionary passed to the template.
        which:
            A factory function that creates a template handler from a list of
            template names.
    """

    # Normalize template name
    if template_name is None:
        name = snake_case(cls.__name__)
        name = '%s/%s' % (cls.__module__.partition('.')[0], name)
        template_names = ['%s.html' % name, '%s.jinja2' % name]
    elif isinstance(template_name, str):
        template_names = [template_name]
    else:
        template_names = template_name

    # Normalize context handling
    if object_context_name is None:
        object_context_names = [snake_case(sub.__name__) for sub in cls.mro()]
    else:
        object_context_names = [object_context_name]

    if get_context is None:
        def get_context(obj):
            return {name: obj for name in object_context_names}

    # Load template
    make_handler = which or make_template_handler
    template_handler = make_handler(template_names)

    # Define implementation inside a closure
    def handler(obj, file):
        context = get_context(obj)
        return template_handler(context, file)

    dump_html.register(cls, handler)


def register_context(cls, *args, **kwargs):
    """
    Decorator that register a template with register_context, but expects a
    context handling function. The decorated function must receive an object
    and return a context dictionary.
    """
    return (
        lambda func:
        register_template(cls, *args, get_context=func, **kwargs) or func
    )


dump_html.register_template = register_template
dump_html.register_context = register_context


def make_template_handler(template_name):
    """
    Make a function that returns a template handler function from a list of
    template name. Template handlers receive a context dictionary and a file
    object and dump data to that object.
    """

    if DEFAULT_HANDLER_FACTORY is not None:
        return DEFAULT_HANDLER_FACTORY(template_name)

    factory = None
    created_handler = None

    def handler(ctx, file):
        nonlocal factory, created_handler
        if DEFAULT_HANDLER_FACTORY is None:
            raise RuntimeError(
                'Template rendering function was not configured. Please execute\n'
                'hyperpython.set_render_template(function) to set the correct\n'
                'rendering function.'
            )
        elif factory is None:
            factory = DEFAULT_HANDLER_FACTORY(template_name)

        if created_handler is None:
            created_handler = factory(template_name)
        created_handler(ctx, file)

    return handler


def from_jinja2_environment(env):
    """
    Return a template handler_factory bound to the given Jinja2 environment.
    """

    def factory(template_names):
        for name in template_names:
            try:
                template = env.get_template(name)
                break
            except jinja2.TemplateNotFound:
                continue
        else:
            raise ValueError('templates not found: %s' % template_names)

        return lambda ctx, file: template.stream(ctx).dump(file)

    return factory


def django_handler_factory(template_names):
    """
    Return a template handler that integrates with Django's templating system.
    """
    # TODO: specialize handler for jinja templates
    template = django_template(template_names)
    renderer = template.render
    return lambda ctx, file: file.write(renderer(ctx))


def set_default_template_handler(value: callable):
    """
    Sets the default handler factory.
    """
    global DEFAULT_HANDLER_FACTORY
    DEFAULT_HANDLER_FACTORY = value


DEFAULT_HANDLER_FACTORY = None
CONTEXT_HANDLERS_MAP = {
    'django': django_handler_factory,
}
