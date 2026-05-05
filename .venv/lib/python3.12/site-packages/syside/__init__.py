"""Python bindings for parsing and validating SysMLv2 models written in the textual notation."""

import os
from typing import TYPE_CHECKING

from . import _platform

# ruff: noqa: E402
# pylint: disable=wrong-import-position

SUPPORTED_PLATFORM = _platform.check_platform()

from .core import *  # noqa: F403

if not SUPPORTED_PLATFORM:
    print(
        f"Platform check produced a false positive. Use {_platform.ENV_VAR} "
        "environment variable to skip platform checks the next time."
    )

    if "SYSIDE_CI" in os.environ:
        # only fail on build CIs to make sure that platform checks do not
        # generate false positives
        raise RuntimeError("False positive platform check!")

from ._loading import (
    try_load_model as try_load_model,
    load_model as load_model,
    collect_files_recursively as collect_files_recursively,
    ModelError as ModelError,
)  # noqa: F401
from ._loading import (
    get_default_executor as get_default_executor,
    Environment as Environment,
    BaseModel as BaseModel,
    Model as Model,
    DocumentKind as DocumentKind,
)  # noqa: F401
from ._diagnostics import (
    DiagnosticMessage as DiagnosticMessage,
    Diagnostics as Diagnostics,
)  # noqa: F401
from . import json as json

# end-users should not be too concerned about leaks, only leave them on by
# default in our build CI
from . import core

if "SYSIDE_CI" not in os.environ:
    core.debug.set_leak_warnings(False)

if not TYPE_CHECKING:
    # add runtime `Value` type, disable 405 due to star imports
    type Value = (
        int
        | float
        | bool
        | Infinity  # noqa: F405
        | str
        | range
        | Element  # noqa: F405
        | BoundMetaclass  # noqa: F405
        | None
        | list[Value]
    )

    core.Value = Value

__version__: str = core.__version__  # type: ignore # pylint: disable=c-extension-no-member
del core
del os
del TYPE_CHECKING

del _platform
del SUPPORTED_PLATFORM
