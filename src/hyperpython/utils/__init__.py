from .sequences import flatten
from .text import (
    snake_case,
    dash_case,
    safe,
    sanitize,
    escape,
    escape_silent,
    unescape,
    html_natural_attr,
    html_safe_natural_attr,
    STR_TYPES,
)

save_attr = lambda obj, name: lambda f: setattr(obj, name, f) or f
