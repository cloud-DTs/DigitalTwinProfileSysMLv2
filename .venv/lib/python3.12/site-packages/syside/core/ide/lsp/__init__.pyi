"""
LSP structures and types.
"""

from collections.abc import Sequence
import enum

from .... import core


class PositionEncodingKind(enum.Enum):
    """
    LSP position encoding kind. Note that Syside uses Utf-8 internally so it will incur no performance penalty.
    Other encodings will require lazy conversions, however allocations will be avoided whenever possible.

    For Python strings, use Utf32 encoding as that is what is used for string indexing and slicing.

    See `LSP specification <https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#positionEncodingKind>`__
    for more details.
    """

    Utf8 = 0

    Utf16 = 1

    Utf32 = 2

class SemanticTokenModifiers(enum.IntFlag):
    """
    LSP defined semantic token modifiers. Technically, this is not a flag enum but
    ``nanobind`` does not permit arbitrary values otherwise.

    See `LSP specification <https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#semanticTokenModifiers>`__
    and `VS Code docs <https://code.visualstudio.com/api/language-extensions/semantic-highlight-guide#standard-token-types-and-modifiers>`__
    for more details.
    """

    def __repr__(self) -> str:
        """Return repr(self)."""

    __str__ = __repr__

    Declaration = 0

    Definition = 1

    Readonly = 2

    Static = 3

    Deprecated = 4

    Abstract = 5

    Async = 6

    Modification = 7

    Documentation = 8

    DefaultLibrary = 9

class SemanticTokenTypes(enum.IntFlag):
    """
    LSP defined semantic token types. Technically, this is not a flag enum but
    ``nanobind`` does not permit arbitrary values otherwise.

    See `LSP specification <https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#semanticTokenTypes>`__
    and `VS Code docs <https://code.visualstudio.com/api/language-extensions/semantic-highlight-guide#standard-token-types-and-modifiers>`__
    for more details.
    """

    def __repr__(self) -> str:
        """Return repr(self)."""

    __str__ = __repr__

    Namespace = 0

    Type = 1

    Class = 2

    Enum = 3

    Interface = 4

    Struct = 5

    TypeParameter = 6

    Parameter = 7

    Variable = 8

    Property = 9

    EnumMember = 10

    Event = 11

    Function = 12

    Method = 13

    Macro = 14

    Keyword = 15

    Modifier = 16

    Comment = 17

    String = 18

    Number = 19

    Regexp = 20

    Operator = 21

    Decorator = 22

class SemanticTokens:
    def __init__(self, result_id: str | None = None, data: Sequence[int] = []) -> None: ...

    @property
    def result_id(self) -> str | None:
        """
        An optional result id. If provided and clients support delta updating the client
        will include the result id in the next semantic token request. A server can then
        instead of computing all semantic tokens again simply send a delta.
        """

    @result_id.setter
    def result_id(self, arg: str, /) -> None: ...

    @property
    def data(self) -> core.ContainerView[int]:
        """The actual tokens."""

class SemanticTokensDelta:
    def __init__(self, result_id: str | None = None, edits: Sequence[SemanticTokensEdit] = []) -> None: ...

    @property
    def result_id(self) -> str | None: ...

    @result_id.setter
    def result_id(self, arg: str, /) -> None: ...

    @property
    def edits(self) -> core.ContainerView[SemanticTokensEdit]:
        """
        The semantic token edits to transform a previous result into a new result.
        """

class SemanticTokensEdit:
    def __init__(self, start: int, delete_count: int, data: Sequence[int] | None = None) -> None: ...

    @property
    def start(self) -> int:
        """The start offset of the edit."""

    @start.setter
    def start(self, arg: int, /) -> None: ...

    @property
    def delete_count(self) -> int:
        """The count of elements to remove."""

    @delete_count.setter
    def delete_count(self, arg: int, /) -> None: ...

    @property
    def data(self) -> core.ContainerView[int] | None:
        """The elements to insert."""

