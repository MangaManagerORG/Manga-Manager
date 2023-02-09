import abc

from src.Layouts.default_layout import Layout as DefLayout
from src.Layouts.joe_layout import Layout as JoeLayout

layout_factory = {
    "default": JoeLayout,
    "joe": JoeLayout
}


class ILayout(abc.ABC):
    name: str


def add_layout_to_factory(layout: ILayout):
    if layout not in layout_factory:
        layout_factory[layout.name] = layout
