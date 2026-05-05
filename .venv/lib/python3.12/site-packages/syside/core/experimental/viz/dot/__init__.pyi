"""
Submodule for rendering DOT graphs.
"""

from ..... import core


class InterconnectionRenderer:
    """A reusable interconnection renderer to DOT graph."""

    def __init__(self, indent: int = 0) -> None:
        """
        ``InterconnectionRenderer`` constructor.

        ``indent`` argument controls initial indentation, this is primarily useful
        when combining multiple renderers.
        """

    @property
    def indent(self) -> int:
        """Indentation level"""

    @indent.setter
    def indent(self, arg: int, /) -> None: ...

    def render(self, arg: core.experimental.viz.Graph, /) -> str:
        """Render a self-contained interconnection diagram."""

    def render_body(self, arg: core.experimental.viz.Graph, /) -> str:
        """
        Render only the contents of an interconnection diagram, i.e. without the
        surrounding ``digraph``. This can be useful if you want to add your own options
        to the rendered diagram, or insert its contents to another diagram.
        """

class NestedRenderer:
    """
    A reusable nested renderer to DOT graph.

    Note that due to ``dot`` limitations, some labels may not be centred.
    """

    def __init__(self, indent: int = 0) -> None:
        """
        ``NestedRenderer`` constructor.

        ``indent`` argument controls initial indentation, this is primarily useful
        when combining multiple renderers.
        """

    @property
    def indent(self) -> int:
        """Indentation level"""

    @indent.setter
    def indent(self, arg: int, /) -> None: ...

    def render(self, arg: core.experimental.viz.Graph, /) -> str:
        """Render a self-contained nested diagram."""

    def render_body(self, arg: core.experimental.viz.Graph, /) -> str:
        """
        Render only the contents of a nested diagram, i.e. without the
        surrounding ``digraph``. This can be useful if you want to add your own options
        to the rendered diagram, or insert its contents to another diagram. Note that
        there needs to be a ``compound=true`` statement in the root scope to correctly clip
        edges to nodes with nested children.
        """

def render_interconnection(graph: core.experimental.viz.Graph, indent: int = 0) -> str:
    """
    Render a self-contained interconnection diagram.

    If rendering multiple diagrams, prefer reusing ``InterconnectionRenderer`` instead to
    improve performance.
    """

def render_interconnection_body(graph: core.experimental.viz.Graph, indent: int = 0) -> str:
    """
    Render only the contents of an interconnection diagram, i.e. without the
    surrounding ``digraph``. This can be useful if you want to add your own options
    to the rendered diagram, or insert its contents to another diagram.

    If rendering multiple diagrams, prefer reusing ``InterconnectionRenderer`` instead to
    improve performance.
    """

def render_nested(graph: core.experimental.viz.Graph, indent: int = 0) -> str:
    """
    Render a self-contained nested diagram.

    If rendering multiple diagrams, prefer reusing ``NestedRenderer`` instead to
    improve performance.
    """

def render_nested_body(graph: core.experimental.viz.Graph, indent: int = 0) -> str:
    """
    Render only the contents of a nested diagram, i.e. without the
    surrounding ``digraph``. This can be useful if you want to add your own options
    to the rendered diagram, or insert its contents to another diagram. Note that
    there needs to be a ``compound=true`` statement in the root scope to correctly clip
    edges to nodes with nested children. 

    If rendering multiple diagrams, prefer reusing ``NestedRenderer`` instead to
    improve performance.
    """

