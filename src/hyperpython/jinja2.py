from jinja2.filters import contextfilter

from hyperpython import render


@contextfilter
def role(ctx, obj, role, **kwargs):
    """
    A filter that renders object according to the given role. In jinja, this
    is accomplished by obj|role('role name')
    """
    try:
        request = ctx['request']
    except KeyError:
        return render(obj, role, **kwargs)
    else:
        return render(obj, role, request=request, **kwargs)


#
# Register filters and global function namespaces
#
filters = {
    'role': role,
}
