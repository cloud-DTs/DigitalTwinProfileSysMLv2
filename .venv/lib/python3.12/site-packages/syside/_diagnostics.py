"""A module providing types for reporting diagnostics."""

from dataclasses import dataclass
import typing

from . import core as syside


@dataclass
class DiagnosticMessage:
    """A diagnostic providing information about a model."""

    filename: str | None
    line: int
    col: int
    severity: syside.DiagnosticSeverity
    code: str
    message: str
    full_message: str

    def __repr__(self) -> str:
        return (
            f"{self.filename or '<source>'}:{self.line}:{self.col}: "
            f"{self.severity.name.lower()} ({self.code}): {self.message}"
        )

    def __str__(self) -> str:
        return self.__repr__()


@dataclass
class Diagnostics:
    """All model diagnostics."""

    parser: list[DiagnosticMessage]
    validation: list[DiagnosticMessage]
    sema: list[DiagnosticMessage]

    @property
    def all(self) -> typing.Generator[DiagnosticMessage, None, None]:
        """Iterate over all diagnostics."""
        yield from self.parser
        yield from self.validation
        yield from self.sema

    def all_with_severity(
        self, severity: syside.DiagnosticSeverity, include_higher_severity: bool = False
    ) -> typing.Generator[DiagnosticMessage, None, None]:
        """Iterate over all diagnostics with the given severity.

        :param severity:
            The severity of diagnostics to iterate over.
        :param include_higher_severity:
            Whether to include diagnostics that are of higher severity than the
            given one.
        """
        for diag in self.all:
            if diag.severity == severity:
                yield diag
            elif include_higher_severity and diag.severity < severity:
                yield diag

    @property
    def errors(self) -> typing.Generator[DiagnosticMessage, None, None]:
        """Iterate over all diagnostics with error severity."""
        return self.all_with_severity(syside.DiagnosticSeverity.Error)

    @property
    def warnings(self) -> typing.Generator[DiagnosticMessage, None, None]:
        """Iterate over all diagnostics with warning severity."""
        return self.all_with_severity(syside.DiagnosticSeverity.Warning)

    @property
    def infos(self) -> typing.Generator[DiagnosticMessage, None, None]:
        """Iterate over all diagnostics with information severity."""
        return self.all_with_severity(syside.DiagnosticSeverity.Information)

    @property
    def hints(self) -> typing.Generator[DiagnosticMessage, None, None]:
        """Iterate over all diagnostics with hint severity."""
        return self.all_with_severity(syside.DiagnosticSeverity.Hint)

    def contains_errors(self, warnings_as_errors: bool = False) -> bool:
        """Checks whether any of the diagnostics contain errors.

        :param warnings_as_errors:
            Treat warnings as errors.
        """
        return any(
            diag.severity == syside.DiagnosticSeverity.Error
            or (
                warnings_as_errors
                and diag.severity == syside.DiagnosticSeverity.Warning
            )
            for diag in self.all
        )

    def __str__(self) -> str:
        return "\n".join(str(diag) for diag in self.all)
