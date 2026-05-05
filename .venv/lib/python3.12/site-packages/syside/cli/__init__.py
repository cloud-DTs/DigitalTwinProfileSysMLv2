#!/usr/bin/env python
"""
Utility that drop the user into an interactive shell with a loaded model.
"""

from collections.abc import Iterable, Generator
import textwrap
from typing import List, Tuple
from pathlib import Path
import logging
import sys

import click

import syside
from ._logger import logger
from .format import format_files, FormatCommandOptions

# mypy: disable-error-code="unused-ignore"


def _all_file_paths(paths: Iterable[Path]) -> Generator[Path]:
    """
    Yields all non-directory paths in ``paths``, as well as all valid source file paths inside
    any directory path in ``paths``.
    """
    for path in paths:
        if path.is_dir():
            yield from syside.collect_files_recursively(path)
        else:
            yield path


def _try_load_from_files(
    paths: Iterable[Path], werror: bool
) -> Tuple[syside.Model, syside.Diagnostics]:
    """
    Tries to load a model from a set of **file** ``paths``. If ``werror`` is set, also exits in
    case of any (model) warnings.
    """

    (model, diagnostics) = syside.try_load_model(paths=paths)

    for diag in diagnostics.all:
        match diag.severity:
            case syside.DiagnosticSeverity.Error:
                logger.error(diag.full_message)
            case syside.DiagnosticSeverity.Warning:
                logger.warning(diag.full_message)
            case syside.DiagnosticSeverity.Information | syside.DiagnosticSeverity.Hint:
                logger.info(diag.full_message)
            case other:
                raise NotImplementedError(f"Unknown diagnostic severity {other}")

    if diagnostics.contains_errors(werror):
        sys.exit(1)

    return (model, diagnostics)


def _embedded_session(model: syside.Model, diagnostics: syside.Diagnostics) -> None:
    """
    Runs an embedded IPython session in the current environment.
    """

    banner = textwrap.dedent(
        """\
        Welcome to isyside!
        
        This is an interactive Python shell with the loaded model accessible as model.
        Builtin modules:        syside
        Convenience variables:  model, diagnostics
        """
    )

    namespace = {"syside": syside, "model": model, "diagnostics": diagnostics}

    try:
        # pylint: disable=import-outside-toplevel
        import IPython  # type: ignore

        IPython.start_ipython(  # type: ignore # untyped
            argv=[f'--InteractiveShell.banner2="{banner}"'],
            header=banner,
            user_ns=namespace,
        )
    except ModuleNotFoundError:
        import code  # pylint: disable=import-outside-toplevel

        code.interact(banner=banner, local=namespace)


CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option("--verbose/--no-verbose", "-v", default=False)
@click.version_option(version=syside.__version__, prog_name="syside")
def cli(verbose: bool) -> None:
    """
    Syside Pro command line utility
    """
    logger.setLevel(logging.INFO if verbose else logging.WARNING)


@cli.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.option("-Werror", is_flag=True, default=False)
def interactive(paths: List[Path], werror: bool) -> None:
    """Drop into an interactive shell with a loaded model"""

    file_paths = list(_all_file_paths(paths))

    logger.info("Including %s files", len(file_paths))

    (model, diagnostics) = _try_load_from_files(file_paths, werror=werror)

    _embedded_session(model, diagnostics)


@cli.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.option("-Werror", is_flag=True, default=False)
def check(paths: List[Path], werror: bool) -> None:
    """
    Checks model for errors/warnings, has exit code 1 if there is an error or if -Werror is set and
    there is a warning.
    """

    file_paths = list(_all_file_paths(paths))

    logger.info("Checking %s files", len(file_paths))

    _ = _try_load_from_files(file_paths, werror=werror)

    click.echo("Checks passed!")


@cli.command(name="format")  # clashes with builtin format
@click.argument("paths", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.option(
    "--check",
    "do_check",
    is_flag=True,
    default=False,
    help=(
        "Avoid writing any formatted files back; instead, exit with a "
        "non-zero status code if any files would have been modified, and zero otherwise"
    ),
)
@click.option(
    "--line-length", default=100, show_default=True, help="Set the line-length"
)
def format_command(paths: list[Path], do_check: bool, line_length: int) -> None:
    """
    Run Syside formatter on the given files or directories.
    """

    file_paths = list(_all_file_paths(paths))

    logger.setLevel(logging.INFO)
    logger.debug("Formatting %s files", len(file_paths))

    sys.exit(
        format_files(
            file_paths,
            FormatCommandOptions(
                check=do_check,
                line_length=line_length,
            ),
        )
    )
