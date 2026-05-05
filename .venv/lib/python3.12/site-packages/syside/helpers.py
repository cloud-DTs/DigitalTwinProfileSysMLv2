"""Helper functions for working with SysMLv2 models."""

from typing import Iterable

import syside


def qualified_name_to_str(qualified_name: Iterable[str] | syside.QualifiedName) -> str:
    """Merge a qualified name into a single string."""
    if isinstance(qualified_name, syside.QualifiedName):
        # QualifiedName also adds quotes around unrestricted identifiers
        return str(qualified_name)
    return "::".join(qualified_name)
