"""
Submodule for IDE related functions.
"""

from typing import overload

from . import lsp as lsp
from .lsp import (
    PositionEncodingKind as PositionEncodingKind,
    SemanticTokenModifiers as SemanticTokenModifiers,
    SemanticTokenTypes as SemanticTokenTypes
)
from ... import core


class AbsoluteSemanticToken:
    """Semantic token using absolute positions."""

    def __init__(self, line: int, character: int, length: int, type: int, modifiers: SemanticTokenModifiersSet) -> None: ...

    @property
    def line(self) -> int:
        """Line where the token starts."""

    @line.setter
    def line(self, arg: int, /) -> None: ...

    @property
    def character(self) -> int:
        """Character where the token starts."""

    @character.setter
    def character(self, arg: int, /) -> None: ...

    @property
    def length(self) -> int:
        """Number of bytes this token extends."""

    @length.setter
    def length(self, arg: int, /) -> None: ...

    @property
    def type(self) -> int:
        """Encoded semantic token type."""

    @type.setter
    def type(self, arg: int, /) -> None: ...

    @property
    def modifiers(self) -> SemanticTokenModifiersSet:
        """Set of semantic token modifiers."""

    @modifiers.setter
    def modifiers(self, arg: SemanticTokenModifiersSet, /) -> None: ...

    def __str__(self) -> str: ...

    def __eq__(self, arg: object, /) -> bool:
        pass

    def __ne__(self, arg: object, /) -> bool:
        pass

    __cpp_name__: str = 'syside::ide::AbsoluteSemanticToken'

class DeltaSemanticToken:
    """Semantic token using delta encoded positions."""

    def __init__(self, delta_line: int, delta_character: int, length: int, type: int, modifiers: SemanticTokenModifiersSet) -> None: ...

    @property
    def delta_line(self) -> int:
        """Number of lines after the previous semantic token start line."""

    @delta_line.setter
    def delta_line(self, arg: int, /) -> None: ...

    @property
    def delta_character(self) -> int:
        """
        Character where the token starts if ``line != 0``, else the number of characters
        after the previous semantic token start character.
        """

    @delta_character.setter
    def delta_character(self, arg: int, /) -> None: ...

    @property
    def length(self) -> int:
        """Number of bytes this token extends."""

    @length.setter
    def length(self, arg: int, /) -> None: ...

    @property
    def type(self) -> int:
        """Encoded semantic token type."""

    @type.setter
    def type(self, arg: int, /) -> None: ...

    @property
    def modifiers(self) -> SemanticTokenModifiersSet:
        """Set of semantic token modifiers."""

    @modifiers.setter
    def modifiers(self, arg: SemanticTokenModifiersSet, /) -> None: ...

    def __str__(self) -> str: ...

    def __eq__(self, arg: object, /) -> bool:
        pass

    def __ne__(self, arg: object, /) -> bool:
        pass

    __cpp_name__: str = 'syside::ide::DeltaSemanticToken'

class SemanticTokenModifiersSet:
    """
    Fixed-size bitset of SemanticTokenModifiers for easier use with LSP serialization.
    """

    @overload
    def __init__(self) -> None:
        """Construct an empty set."""

    @overload
    def __init__(self, arg: int, /) -> None:
        """Construct set from an unsigned integer."""

    def __int__(self) -> int: ...

    @staticmethod
    def __len__() -> int: ...

    @overload
    def __getitem__(self, arg: lsp.SemanticTokenModifiers, /) -> bool: ...

    @overload
    def __getitem__(self, arg: int, /) -> bool: ...

    @overload
    def __setitem__(self, arg0: lsp.SemanticTokenModifiers, arg1: bool, /) -> None: ...

    @overload
    def __setitem__(self, arg0: int, arg1: bool, /) -> None: ...

    def __str__(self) -> str: ...

    def __eq__(self, arg: object, /) -> bool:
        pass

    def __ne__(self, arg: object, /) -> bool:
        pass

    __cpp_name__: str = 'syside::ide::SemanticTokenModifiersSet'

class SemanticTokensBuilder:
    """Helper for building LSP compatible semantic tokens."""

    def __init__(self) -> None: ...

    def append(self, arg: AbsoluteSemanticToken, /) -> None:
        """Append a new semantic token."""

    @property
    def id(self) -> int:
        """Randomly generated ID of this builder."""

    @property
    def absolute_tokens(self) -> core.ContainerView[AbsoluteSemanticToken]:
        """
        Get all collected absolute semantic tokens. Note that this may require
        decoding delta tokens first.
        """

    @property
    def delta_tokens(self) -> core.ContainerView[DeltaSemanticToken]:
        """
        Get all collected delta semantic tokens. Note that in case tokens were
        appended out of order, an encoding may take place.
        """

    @property
    def previous_tokens(self) -> core.ContainerView[DeltaSemanticToken]:
        """
        Get previously built tokens as delta tokens. Must call ``previous_result`` to make this available.
        """

    @overload
    def previous_result(self, arg: int, /) -> None:
        """
        Move the contents of this builder to previous result and reset the state. If id
        does not match ``id``, current tokens are discarded instead. This must be called before building edits.
        """

    @overload
    def previous_result(self, arg: str, /) -> None:
        """
        Overload of ``previous_result`` that will parse the provided id to int.
        """

    def build(self) -> lsp.SemanticTokens:
        """Build currently collected semantic tokens into LSP compatible format."""

    def build_edits(self) -> lsp.SemanticTokens | lsp.SemanticTokensDelta:
        """
        Build currently collected semantic tokens into LSP compatible format.
        If ``can_build_edits``, a delta to the ``previous_tokens`` will be returned
        which will usually be smaller than the full tokens.
        """

    @property
    def can_build_edits(self) -> bool:
        """
        Returns ``true`` if ``build_edits`` would return delta to the previous result.
        """

    __cpp_name__: str = 'syside::ide::SemanticTokensBuilder'

def build_delta_semantic_tokens(document: core.Document, id: int | str, encoding: lsp.PositionEncodingKind = lsp.PositionEncodingKind.Utf8, multiline_tokens: bool = True, builder: SemanticTokensBuilder | None = None) -> SemanticTokensBuilder | None:
    """
    Build full document semantic tokens for edits. Returns ``builder`` if successful, and ``None`` otherwise. Generally,
    ``None`` is returned if the ``document`` has nothing to highlight.

    Internally calls :py:meth:`SemanticTokensBuilder.previous_result <syside.ide.SemanticTokensBuilder.previous_result>` before
    building tokens.

    :param document:
        The document to build full semantic tokens for.
    :param id:
        Previous result id. ``previous_result`` is called first, and if the ``id`` matches ``builder`` id the
        returned ``builder`` can be used to build edits.
    :param encoding:
        The position encoding to use for semantic tokens. Use Utf32 if interacting with Python strings.
    :param multiline_tokens:
        Whether to keep multiline tokens as is and not split them. Generally used for language clients that do
        not support multiline tokens.
    :param builder:
        The builder to collect semantic tokens into. Note that if provided, its internal state will be reset.
    :return:
        Provided ``builder``, or new one otherwise, if there was anything to highlight.
    :raises ValueError:
        If ``encoding != Utf8 or not multiline_tokens`` and ``document.text_document is None``. Utf8 encoding
        and ``multiline_tokens`` does not require a text source as all the required information is already
        contained in the CST.
    """

def build_full_semantic_tokens(document: core.Document, encoding: lsp.PositionEncodingKind = lsp.PositionEncodingKind.Utf8, multiline_tokens: bool = True, builder: SemanticTokensBuilder | None = None) -> SemanticTokensBuilder | None:
    """
    Build full document semantic tokens. Returns ``builder`` if successful, and ``None`` otherwise. Generally,
    ``None`` is returned if the ``document`` has nothing to highlight.

    :param document:
        The document to build full semantic tokens for.
    :param encoding:
        The position encoding to use for semantic tokens. Use Utf32 if interacting with Python strings.
    :param multiline_tokens:
        Whether to keep multiline tokens as is and not split them. Generally used for language clients that do
        not support multiline tokens.
    :param builder:
        The builder to collect semantic tokens into. Note that if provided, its internal state will be reset.
    :return:
        Provided ``builder``, or new one otherwise, if there was anything to highlight.
    :raises ValueError:
        If ``encoding != Utf8 or not multiline_tokens`` and ``document.text_document is None``. Utf8 encoding
        and ``multiline_tokens`` does not require a text source as all the required information is already
        contained in the CST.
    """

def build_range_semantic_tokens(document: core.Document, range: core.RangeUtf8, encoding: lsp.PositionEncodingKind = lsp.PositionEncodingKind.Utf8, multiline_tokens: bool = True, builder: SemanticTokensBuilder | None = None) -> SemanticTokensBuilder | None:
    """
    Build range document semantic tokens. Returns ``builder`` if successful, and ``None`` otherwise. Generally,
    ``None`` is returned if the ``document`` has nothing to highlight.

    The returned ``builder`` will contain tokens encompassing ``range``. For most documents, this will
    be more efficient that building full semantic tokens.

    :param document:
        The document to build range semantic tokens for.
    :param range:
        Range that should have all tokens highlighted. Implementation may return also build tokens
        outside of this range.
    :param encoding:
        The position encoding to use for semantic tokens. Use Utf32 if interacting with Python strings.
    :param multiline_tokens:
        Whether to keep multiline tokens as is and not split them. Generally used for language clients that do
        not support multiline tokens.
    :param builder:
        The builder to collect semantic tokens into. Note that if provided, its internal state will be reset.
    :return:
        Provided ``builder``, or new one otherwise, if there was anything to highlight.
    :raises ValueError:
        If ``encoding != Utf8 or not multiline_tokens`` and ``document.text_document is None``. Utf8 encoding
        and ``multiline_tokens`` does not require a text source as all the required information is already
        contained in the CST.
    """

