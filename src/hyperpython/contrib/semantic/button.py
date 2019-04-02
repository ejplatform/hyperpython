import hyperpython as hp
import hyperpython.components as hpc
from hyperpython.components import elem_or_span
from hyperpython.contrib.semantic.base import component

SOCIAL_NETWORKS = {
    "facebook": "Facebook",
    "twitter": "Twitter",
    "google plus": "Google+",
    "vk": "VK",
    "linkedin": "LinkedIn",
    "instagram": "Instagram",
    "youtube": "YouTube",
}

button = component(
    hpc.a_or_button,
    [  # Roles
        "basic",
        "primary",
        "secondary",
        # Mood
        "positive",
        "negative",
        # Presentation
        "inverted",
        "compact",
        "toggle",
        "fluid",
        "circular",
        # State
        "active",
        "disabled",
        "loading",
        # Size
        "mini",
        "tiny",
        "small",
        "medium",
        "large",
        "big",
        "huge",
        "massive",
        # Colors
        "red",
        "orange",
        "yellow",
        "olive",
        "green",
        "teal",
        "blue",
        "violet",
        "purple",
        "pink",
        "brown",
        "grey",
        "black",
    ],
    prefix_classes=["ui"],
    suffix_classes=["button"],
)


# TODO: float='left/right' => 'left/right floated'


def social_button(which, text=None, icon=None, **kwargs):
    if which not in SOCIAL_NETWORKS:
        raise ValueError("invalid social network.")
    icon = icon or which
    text = text or [hp.i(class_=[icon, "icon"]), SOCIAL_NETWORKS[which]]
    return button(text, class_=which)


def buttons():
    raise NotImplementedError


def animated_button(first, second, animation=None, **kwargs):
    classes = ["animated"]
    if animation:
        classes.append(animation)
    children = [
        elem_or_span(first).add_class(["visible", "content"]),
        elem_or_span(second).add_class(["hidden", "content"]),
    ]
    return button(children, **kwargs).add_class(classes)
