"""
Internal utility module to perform basic platform checks for common system
issues before attempting to load the native module.
"""

import os
import platform
import shutil
import textwrap
import warnings
from dataclasses import dataclass

from . import _build_info

ENV_VAR = "SYSIDE_NO_PLATFORM_CHECK"
MESSAGE_LINE_LENGTH = 79
LAZY_NEWLINE = "⏎"

# there is no ctypes.windll on linux/darwin so just disable them
# mypy: disable-error-code="arg-type, attr-defined"
# pylint: disable=line-too-long,import-outside-toplevel,missing-class-docstring
# pyright: reportAttributeAccessIssue=false


def rewrap_message(message: str) -> str:
    """
    Format the message to have lines of length at most ``MESSAGE_LINE_LENGTH``.
    """
    paragraphs = (
        textwrap.dedent(message).strip().replace(LAZY_NEWLINE, "\n").split("\n\n")
    )
    return "\n\n".join(
        textwrap.fill(
            paragraph,
            width=MESSAGE_LINE_LENGTH,
            break_long_words=False,
            break_on_hyphens=False,
        )
        for paragraph in paragraphs
    )


def _show_warning(message: str, stacklevel: int = 1) -> None:
    """
    Show a warning with the message formatted to have lines of length at most
    ``MESSAGE_LINE_LENGTH``.
    """
    warnings.warn(
        rewrap_message(message), category=RuntimeWarning, stacklevel=stacklevel + 1
    )


@dataclass
class UnsupportedPlatformError:
    """
    Result of the platform check indicating that the platform is not supported.
    """

    message: str
    """
    Message explaining the reason why the platform is not supported and what to
    do about it.
    """

    def show_as_warning(self) -> None:
        """
        Show this error as a Python warning.
        """
        _show_warning(self.message, stacklevel=2)


def _check_newer(version: str, build_version: str, exact_major: bool) -> bool:
    if not build_version:
        _show_warning("Unknown Syside system libraries version.", stacklevel=2)
        return True

    left, right = version.split("."), build_version.split(".")

    majors = int(left[0]), int(right[0])
    if majors[0] != majors[1]:
        return not exact_major and majors[0] > majors[1]

    # Minor must be greater
    return int(left[1]) >= int(right[1])


WINDOWS_ARCHS = {
    "AMD64",
    # maybe in the future
    # "ARM64",
}


def check_windows() -> UnsupportedPlatformError | None:  # pylint: disable=too-many-locals
    """
    Checks whether Windows is supported.

    :return: ``UnsupportedPlatformError`` if the platform is not supported,
        ``None`` otherwise.
    """

    machine = platform.machine()
    if machine not in WINDOWS_ARCHS:
        supported_architectures = ", ".join(WINDOWS_ARCHS)
        return UnsupportedPlatformError(
            f"""
                Unsupported Windows architecture: {machine}.

                Supported architectures: {supported_architectures}
            """,
        )

    version = platform.version().split(".", 1)[0]
    try:
        if int(version) >= 10:
            return None
    except TypeError:
        return UnsupportedPlatformError(
            """
                Windows 10 is the minimum supported version, this may lead to
                the native module load failure.
            """
        )

    return None


def _find_libc_version_slow() -> str | UnsupportedPlatformError:
    import ctypes.util
    import re
    import subprocess

    libc = ctypes.util.find_library("c")

    if not libc:
        return UnsupportedPlatformError(
            """
                Could not find libc, this may lead to the native module load
                failure.
            """,
        )

    compiler = shutil.which("gcc") or shutil.which("clang")
    if compiler:
        result = subprocess.run(
            [compiler, f"--print-file-name={libc}"],
            stdout=subprocess.PIPE,
            check=False,
        )
    else:
        return UnsupportedPlatformError(
            """
                Neither gcc nor clang compiler was found to check the libc
                version.

                Incorrect libc version may lead to the native module load
                failure.
            """,
        )
    if result.returncode == 0:
        libc_path = result.stdout.decode().strip()
    else:
        return UnsupportedPlatformError(
            f"""
                Failed to run {compiler} to check the libc version.

                Incorrect libc version may lead to the native module load
                failure.
            """,
        )

    result = subprocess.run(
        [libc_path],
        stdout=subprocess.PIPE,
        check=False,
    )
    if result.returncode == 0:
        match = re.search(r"version\s*(\d+\.\d+)", result.stdout.decode())
        if match:
            return match.group(1)

    return UnsupportedPlatformError(
        f"""
            Failed to retrieve the libc version from {libc_path}.

            Incorrect libc version may lead to the native module load
            failure.
        """,
    )


def _find_libc_version() -> str | UnsupportedPlatformError:
    import re

    # NB: platform.libc_ver() may return a different version than the system
    # libc so do not use it. It scans the given executable for the version it
    # was linked against, rather than the version that is available on the
    # system. `platform.platform()` seems to include the `glibc` version in the
    # returned string, at least on Arch, Debian, and Ubuntu.
    plat = re.search(r"libc(\d+\.\d+)", platform.platform())
    if plat is not None:
        return plat.group(1)

    return _find_libc_version_slow()


def check_linux() -> UnsupportedPlatformError | None:
    """
    Checks whether Linux is supported.

    :return: ``UnsupportedPlatformError`` if the platform is not supported,
        ``None`` otherwise.
    """

    version = _find_libc_version()

    if isinstance(version, UnsupportedPlatformError):
        return version

    if not version or not _check_newer(
        version, _build_info.BUILD_LIBC, exact_major=True
    ):
        build_libc = _build_info.BUILD_LIBC
        return UnsupportedPlatformError(
            f"""
                Your system contains an older libc version ({version} <
                {build_libc}) than Syside was linked to. This may lead to the
                native module load failure.
            """,
        )

    return None


def check_darwin() -> UnsupportedPlatformError | None:
    """
    Checks whether Mac OS is supported.

    :return: ``UnsupportedPlatformError`` if the platform is not supported,
        ``None`` otherwise.
    """
    supported = {"arm64", "x86_64"}
    version, _, arch = platform.mac_ver()

    if arch not in supported:
        supported_architectures = ", ".join(supported)
        return UnsupportedPlatformError(
            f"""
                Unsupported Darwin architecture {arch}, supported architectures
                are {supported_architectures}, this may lead to the native
                module load failure.
            """,
        )

    if not _check_newer(version, _build_info.BUILD_OSX_VERSION, exact_major=False):
        build_osx_version = _build_info.BUILD_OSX_VERSION
        return UnsupportedPlatformError(
            f"""
                Darwin version is older than Syside build version ({version} <
                {build_osx_version}), this may lead to the native module load
                failure.
            """,
        )

    return None


def check_platform() -> bool:
    """
    Minimal platform check that returns ``True`` if native Syside module will be
    loaded without errors. ``False`` return value does not guarantee load
    failure.
    """

    if ENV_VAR in os.environ:
        # escape hatch for when platform check gives false positives
        return True

    name = platform.system()

    try:
        match name:
            case "Linux":
                result = check_linux()
            case "Windows":
                result = check_windows()
            case "Darwin":
                result = check_darwin()
            case _:
                _show_warning(f"Unsupported platform: {name}")
                return False
    except Exception as exc:  # pylint: disable=broad-exception-caught
        _show_warning(
            f"""
                An unexpected error occurred while checking platform capability:
                {exc}. This may lead to the native module load failure.
            """
        )
        return False
    if result is None:
        return True
    result.show_as_warning()
    return False
