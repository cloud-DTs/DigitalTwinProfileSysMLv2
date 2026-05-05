"""
Python implementation of minimal format CLI command
"""

from dataclasses import dataclass
import pathlib
from typing import Iterable


from .. import core as syside
from .._loading import get_default_executor, _create_user_documents, _create_documents
from ._logger import logger


def parse_files(
    files: Iterable[str | pathlib.Path],
) -> tuple[
    syside.ExecutionResult,
    list[syside.SharedMutex[syside.Document]],
    syside.TextDocuments,
]:
    """Parse ``files`` into documents.

    Args:
        files: file paths to parse as KerML/SysML documents

    Returns:
        ``tuple`` of ``result`` containing diagnostics, list of parsed documents and
        a registry of ``TextDocument`` for use in formatting diagnostics.
    """
    executor = get_default_executor()
    text_documents = syside.TextDocuments.create_st()
    texts = _create_user_documents(
        executor, (pathlib.Path(f) for f in files), None, None, False, text_documents
    )
    documents = _create_documents(texts, syside.DocumentTier.Project)

    pipeline = syside.make_pipeline(syside.PipelineOptions())
    schedule = pipeline.schedule(
        documents,
        syside.ScheduleOptions(
            validation_timing=syside.ValidationTiming.Never,
            # save time by doing bare minimum needed to format files
            cutoff=syside.BuildState.Parsed,
            # attach comments (notes as KerML/SysML calls them) to preserve them
            attach_comments=True,
        ),
    )

    return executor.run(schedule), documents, text_documents


@dataclass
class FormatCommandOptions:
    """All options accepted by format CLI command"""

    check: bool
    line_length: int = 100


def format_files(
    files: Iterable[str | pathlib.Path], options: FormatCommandOptions
) -> int:
    """
    Format KerML and SysML files at ``files`` with ``options``.

    Returns:
        exit code, 0 if succeeded, 1 otherwise
    """
    result, documents, text_documents = parse_files(files)

    if not result:
        result.rethrow_exception()

    valid_syntax = True
    report_options = syside.DiagnosticFormatOptions(
        colours=True, draw_tree=syside.TreeDrawing.Unicode
    )
    for document, diagnostics in zip(result.documents, result.diagnostics):
        if diagnostics.passed():
            continue

        valid_syntax = False
        with document.lock() as locked:
            text = locked.text_document
            assert text  # never None
            with text.lock() as src:
                ctx = syside.DiagnosticContext(
                    source=src.text,
                    filename=syside.decode_path(locked.url),
                    related_sources=text_documents,
                )

            logger.error(
                syside.format_diagnostics(diagnostics.parser, ctx, report_options)
            )

    if not valid_syntax:
        logger.error("❌ Syntax errors found, not formatting!")
        return 1

    printer = syside.ModelPrinter.kerml()
    unformatted = 0
    config = syside.PrinterConfig(line_width=options.line_length)
    for document in documents:
        with document.lock() as locked:
            if locked.language == "sysml":
                printer.mode = syside.PrintMode.SysML
            else:
                printer.mode = syside.PrintMode.KerML
            formatted = syside.pprint(locked.root_node, printer, config)

            text = locked.text_document
            assert text  # never None
            with text.lock() as src:
                is_formatted = src.text == formatted

            if is_formatted:
                continue

            unformatted += 1

            path = syside.decode_path(locked.url)
            if options.check:
                logger.info("Would reformat: %s", path)
                continue

            with open(path, "w", encoding="utf-8") as file:
                file.write(formatted)

    if unformatted > 0:
        if options.check:
            logger.error(
                "❌ %d out of %d files would be formatted.", unformatted, len(documents)
            )
            return 1

        logger.info("%d out of %d files formatted.", unformatted, len(documents))
    else:
        logger.info("%d files already formatted.", len(documents))

    return 0
