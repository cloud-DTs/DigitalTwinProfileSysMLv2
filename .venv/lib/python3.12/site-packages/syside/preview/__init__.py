"""
Module implementing various proposals for how to make the Syside API
more convenient and easier to pick up.
"""

from ..core import *
from .._loading import (
    ModelError as ModelError,
)  # noqa: F401
from .._diagnostics import (
    DiagnosticMessage as DiagnosticMessage,
    Diagnostics as Diagnostics,
)  # noqa: F401
from ._loading import (
    empty_model as empty_model,
    open_model as open_model,
    open_model_unlocked as open_model_unlocked,
    LockedModel as LockedModel,
    UnlockedModel as UnlockedModel,
)  # noqa: F401
