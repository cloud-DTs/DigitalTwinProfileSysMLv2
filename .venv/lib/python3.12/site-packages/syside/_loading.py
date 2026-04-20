"""Module with functions for loading SysMLv2 models."""

from dataclasses import dataclass
import enum
import os
import pathlib
import typing

from . import core as syside
from ._diagnostics import DiagnosticMessage, Diagnostics

__DEFAULT_EXECUTOR: list[syside.Executor] = []


class Environment:
    """
    Standard library environment for use with user models.
    """

    def __init__(
        self,
        documents: list[syside.SharedMutex[syside.Document]],
        index: syside.StaticIndex,
        lib: syside.Stdlib,
        result: syside.ExecutionResult | None,
    ):
        self.documents: list[syside.SharedMutex[syside.Document]] = documents
        """Documents in this environment"""
        self.__index: syside.StaticIndex = index
        self.lib: syside.Stdlib = lib
        """Standard library cache"""
        self.result: syside.ExecutionResult | None = result
        """Result of parsing documents in this environment"""

    _STDLIB: "Environment | None" = None

    @classmethod
    def get_default(cls) -> "Environment":
        """
        Get a default constructed standard library environment. This will only be
        executed on the first call, and any subsequent calls will return a cached
        value. Standard library environment is cached based on the assumption that
        it **WILL NOT** change during runtime, saving resources when loading other
        models.
        """

        if not cls._STDLIB:
            stdlib_files = get_stdlib_files()
            environment = cls.from_stdlib_files(stdlib_files)
            cls._STDLIB = environment
        return cls._STDLIB

    @classmethod
    def from_stdlib_files(cls, stdlib_files: list[pathlib.Path]) -> "Environment":
        """
        Construct the environment from the given stdlib files.

        :param stdlib_files:
            The paths to SysMLv2 or KerML files representing the stdlib. These
            files must have correct file extensions (``.sysml`` or ``.kerml``).
        """
        executor = get_default_executor()
        stdlib_io_result = _create_stdlib_documents(
            executor, stdlib_files, use_low_level_loading_api=False
        )
        stdlib_docs = _create_documents(
            stdlib_io_result, syside.DocumentTier.StandardLibrary
        )
        lib = syside.Stdlib()
        index = syside.StaticIndex()
        result = _build_model(executor, lib, stdlib_docs, index)
        return cls(stdlib_docs, index, lib, result)

    @classmethod
    def from_documents(
        cls,
        documents: typing.Iterable[syside.SharedMutex[syside.Document]],
        index: syside.StaticIndex | None = None,
    ) -> "Environment":
        """
        Construct the environment from the given documents.

        :param documents:
            The documents from which to construct the SysMLv2 environment.
        :param index:
            The index to be used in models. If ``None``, creates a new index. If
            not ``None``, clones the index to avoid mutating the argument.
        """
        base_docs = list(documents)
        executor = get_default_executor()
        lib = syside.Stdlib()
        if index is None:
            index = syside.StaticIndex()
        else:
            index = index.clone()
        for document in base_docs:
            with document.lock() as locked:
                if locked.build_state >= syside.BuildState.Indexed:
                    index.insert(locked)
        result = _build_model(executor, lib, base_docs, index)
        return cls(base_docs, index, lib, result)

    def index(self) -> syside.StaticIndex:
        """
        Returns a copy of the environment index for use in dependent models. A
        copy is required so that dependent models do not affect this environment
        and other dependent models.
        """
        return self.__index.clone()


class DocumentKind(enum.Enum):
    """Is this a model-created document?"""

    MODEL = "model"
    """The document was created for this model."""

    ENVIRONMENT = "environment"
    """The document is from the environment."""

    ALL = "all"
    """The document is from either."""

    # for backwards compat
    USER = MODEL
    STDLIB = ENVIRONMENT


@dataclass
class BaseModel:
    """A SysMLv2 model represented using abstract syntax."""

    result: syside.ExecutionResult | None
    """The model build result as returned by core module."""
    environment: Environment
    """The environment this model was built in"""
    documents: list[syside.SharedMutex[syside.Document]]
    """Documents as part of this model."""
    lib: syside.Stdlib
    """Standard library cache"""
    index: syside.StaticIndex
    """Index of exported symbols"""

    @property
    def all_docs(self) -> list[syside.SharedMutex[syside.Document]]:
        """All built documents, including standard library."""
        return self.environment.documents + self.user_docs

    @property
    def stdlib_docs(self) -> list[syside.SharedMutex[syside.Document]]:
        """
        Environment documents as part of this model. Prefer accessing
        documents through 'environment' instead
        """
        return self.environment.documents

    @property
    def user_docs(self) -> list[syside.SharedMutex[syside.Document]]:
        """User documents built as part of this model. Prefer 'documents' instead."""
        return self.documents

    def _get_documents(
        self, kind: DocumentKind = DocumentKind.MODEL
    ) -> typing.Iterable[syside.SharedMutex[syside.Document]]:
        match kind:
            case DocumentKind.MODEL:
                yield from self.documents
            case DocumentKind.ENVIRONMENT:
                yield from self.environment.documents
            case DocumentKind.ALL:
                yield from self.environment.documents
                yield from self.documents
            case _:
                raise ValueError(f"Unexpected document kind: {kind}")

    def uris(
        self, considered_document_kinds: DocumentKind = DocumentKind.MODEL
    ) -> typing.Iterable[str]:
        """Return URIs of documents.

        :param considered_document_kinds:
            What document kinds to consider. By default returns only documents
            created for this model.
        """
        for doc in self._get_documents(considered_document_kinds):
            with doc.lock() as locked:
                url = locked.url
            yield syside.decode_path(url)

    def nodes(
        self,
        node_kind: type[syside.TElement],
        include_subtypes: bool = False,
        considered_document_kinds: DocumentKind = DocumentKind.MODEL,
    ) -> typing.Iterable[syside.TElement]:
        """Iterate over all nodes of the given kind.

        :param node_kind:
            What kind of nodes to return.
        :param include_subtypes:
            Whether to consider subtypes.
        :param considered_document_kinds:
            What document kinds to consider. By default returns only documents
            created for this model.
        """
        for doc in self._get_documents(considered_document_kinds):
            with doc.lock() as locked:
                if include_subtypes:
                    yield from locked.all_nodes(node_kind)
                else:
                    yield from locked.nodes(node_kind)

    def elements(
        self,
        node_kind: type[syside.TElement],
        include_subtypes: bool = False,
        considered_document_kinds: DocumentKind = DocumentKind.MODEL,
    ) -> typing.Iterable[syside.TElement]:
        """An alias for nodes."""
        return self.nodes(node_kind, include_subtypes, considered_document_kinds)

    def to_environment(self) -> Environment:
        """
        Convert this model to ``Environment`` for building other dependent
        models.
        """
        return Environment(self.all_docs, self.index, self.lib, self.result)


@dataclass
class Model(BaseModel):
    """A SysMLv2 model represented using abstract syntax."""

    result: syside.ExecutionResult
    """The model build result as returned by core module."""


def get_default_executor() -> syside.Executor:
    """
    Get a default initialized ``Executor`` for running schedules. Default
    executor will use half the logical cores that are available on the current
    machine. An executor is just a thread pool so there is no reason for
    constructing and destroying one all the time.
    """
    # another option is to use lru_cache but it destroys the function signature
    # allowing any arguments during static analysis, this way we get static
    # analyser warnings when calling this function with any parameters
    if not __DEFAULT_EXECUTOR:
        executor = syside.Executor(int((os.cpu_count() or 2) / 2))
        # multithreading for GC is highly beneficial, no reason not to use
        syside.gc.set_executor(executor)
        __DEFAULT_EXECUTOR.append(executor)
    return __DEFAULT_EXECUTOR[0]


def collect_files_recursively(
    directory_path: str | os.PathLike[typing.Any],
) -> list[pathlib.Path]:
    """
    Recursively collect all ``.sysml`` and ``.kerml`` files in the specified
    directory.
    """
    directory_path = pathlib.Path(directory_path)
    if not directory_path.exists():
        raise ValueError(f"Directory does not exist: {directory_path}")
    if not directory_path.is_dir():
        raise ValueError(f"Path is not a directory: {directory_path}")
    files = [
        path
        for path in directory_path.rglob("*.*ml")
        if path.suffix in (".sysml", ".kerml")
    ]
    return files


def get_stdlib_files() -> list[pathlib.Path]:
    """Return paths to the stdlib files shipped together with Syside."""
    stdlib = pathlib.Path(__file__).parent / "sysml.library"
    stdlib_files = collect_files_recursively(stdlib)
    assert stdlib_files, "Installation is corrupted, standard library is missing."
    return stdlib_files


def _create_diagnostics(
    syside_diagnostics: typing.Iterable[syside.Diagnostic],
    ctx: syside.DiagnosticContext,
    options: syside.DiagnosticFormatOptions,
) -> list[DiagnosticMessage]:
    return [
        DiagnosticMessage(
            filename=ctx.filename,
            line=d.segment.range.start.line + 1,
            col=d.segment.range.start.character + 1,
            severity=d.severity,
            code=d.code,
            message=d.message,
            full_message=syside.format_diagnostics([d], ctx, options),
        )
        for d in syside_diagnostics
    ]


def _create_stdlib_documents(
    executor: syside.Executor,
    stdlib_files: typing.Iterable[pathlib.Path],
    use_low_level_loading_api: bool,
) -> list[syside.SharedMutex[syside.TextDocument]]:
    if use_low_level_loading_api:
        stdlib_io = syside.IOSchedule.make_empty_schedule(True)
        for file in stdlib_files:
            # This should never fail but sometime on Windows ``add_file`` fails with
            # path does not exist message...
            assert file.exists(), f"File does not exist: {file}"
            stdlib_io.add_file(file, file.suffix[1:].lower())
        return executor.run(stdlib_io)[1]
    text_documents = syside.TextDocuments.create_st()
    documents = []
    for path in stdlib_files:
        language = path.suffix[1:].lower()
        with open(path, encoding="utf-8") as fp:
            content = fp.read()
        file_url = syside.make_file_url(path)
        text_document = text_documents.open(file_url, language, content, 0)
        documents.append(text_document)
    return documents


def _create_user_documents(
    executor: syside.Executor,
    user_paths: typing.Iterable[pathlib.Path],
    sysml_source: str | None,
    kerml_source: str | None,
    use_low_level_loading_api: bool,
    text_documents: syside.TextDocuments | None = None,
) -> list[syside.SharedMutex[syside.TextDocument]]:
    if use_low_level_loading_api:
        user_io = syside.IOSchedule.make_empty_schedule(True)
        if text_documents:
            user_io.text_documents = text_documents
        if user_paths:
            for path in user_paths:
                language = path.suffix[1:].lower()
                user_io.add_file(path, language)
        if sysml_source is not None:
            file_url = syside.Url("memory://sysml_model.sysml")
            user_io.add_source(file_url, sysml_source, "sysml")
        if kerml_source is not None:
            file_url = syside.Url("memory://kerml_model.kerml")
            user_io.add_source(file_url, kerml_source, "kerml")
        return executor.run(user_io)[1]

    if not text_documents:
        text_documents = syside.TextDocuments.create_st()
    user_documents = []
    if user_paths:
        for path in user_paths:
            language = path.suffix[1:].lower()
            with open(path, encoding="utf-8") as fp:
                content = fp.read()
            file_url = syside.make_file_url(path)
            text_document = text_documents.open(file_url, language, content, 0)
            user_documents.append(text_document)
    if sysml_source is not None:
        file_url = syside.Url("memory://sysml_model.sysml")
        text_document = text_documents.open(file_url, "sysml", sysml_source, 0)
        user_documents.append(text_document)
    if kerml_source is not None:
        file_url = syside.Url("memory://kerml_model.kerml")
        text_document = text_documents.open(file_url, "kerml", kerml_source, 0)
        user_documents.append(text_document)
    return user_documents


def _validate_paths(
    paths: typing.Iterable[str | os.PathLike[typing.Any]],
) -> list[pathlib.Path]:
    validated_paths: list[pathlib.Path] = []
    invalid_paths: list[pathlib.Path] = []
    for path in paths:
        path = pathlib.Path(path)
        if path.exists() and path.is_file():
            validated_paths.append(path)
        else:
            invalid_paths.append(path)
    if invalid_paths:
        invalid_paths_str = "\n".join(f"`{path}`" for path in invalid_paths)
        raise ValueError(f"Files do not exist or are directories:\n{invalid_paths_str}")
    return validated_paths


def _validate_parameters(
    paths: typing.Iterable[str | os.PathLike[typing.Any]] | None = None,
    sysml_source: str | None = None,
    kerml_source: str | None = None,
) -> list[pathlib.Path]:
    all_inputs_undefined = (
        paths is None and sysml_source is None and kerml_source is None
    )
    if all_inputs_undefined:
        raise ValueError(
            "At least one of `paths`, `sysml_source`, and `kerml_source` must be defined."
        )
    if paths:
        return _validate_paths(paths)
    return []


def _build_model(
    executor: syside.Executor,
    lib: syside.Stdlib,
    all_docs: typing.Sequence[syside.SharedMutex[syside.Document]],
    index: syside.StaticIndex | None = None,
) -> syside.ExecutionResult:
    if index is None:
        index = syside.StaticIndex()
    pipeline = syside.make_pipeline(syside.PipelineOptions(static_index=index, lib=lib))
    schedule = pipeline.schedule(
        all_docs,
        syside.ScheduleOptions(validation_timing=syside.ValidationTiming.Manual),
    )
    result = executor.run(schedule)
    if not result:
        result.rethrow_exception()
    return result


def _extend_diagnostics(
    result: Diagnostics,
    diags: syside.DiagnosticResults,
    ctx: syside.DiagnosticContext,
    options: syside.DiagnosticFormatOptions,
) -> None:
    if diags.parser:
        result.parser.extend(_create_diagnostics(diags.parser, ctx, options))
    if diags.validation:
        result.validation.extend(_create_diagnostics(diags.validation, ctx, options))
    if diags.sema:
        result.sema.extend(_create_diagnostics(diags.sema, ctx, options))


def _collect_diagnostics(
    documents: typing.Iterable[syside.SharedMutex[syside.BasicDocument]],
    diagnostics: typing.Iterable[syside.DiagnosticResults],
) -> Diagnostics:
    """Check if there were any error and if that is the case create the error object."""
    options = syside.DiagnosticFormatOptions(
        colours=True, draw_tree=syside.TreeDrawing.Unicode
    )
    result = Diagnostics([], [], [])
    for doc_mutex, diags in zip(documents, diagnostics):
        if diags.empty:
            continue

        with doc_mutex.lock() as document:
            text = document.text_document
            filename = syside.decode_path(document.url)
            if text is not None:
                with text.lock() as document_text:
                    ctx = syside.DiagnosticContext(
                        source=document_text.text, filename=filename
                    )
                    _extend_diagnostics(result, diags, ctx, options)
            else:
                ctx = syside.DiagnosticContext(source="", filename=filename)
                _extend_diagnostics(result, diags, ctx, options)
    return result


def _create_documents(
    io_result: typing.Iterable[syside.SharedMutex[syside.TextDocument]],
    tier: syside.DocumentTier,
) -> list[syside.SharedMutex[syside.Document]]:
    documents: list[syside.SharedMutex[syside.Document]] = []
    for text in io_result:
        with text.lock() as text_doc:
            doc = syside.Document.create_st(
                syside.DocumentOptions(
                    url=text_doc.url,
                    language=text_doc.language_id,
                    tier=tier,
                )
            )
        with doc.lock() as document:
            document.text_document = text
        documents.append(doc)
    return documents


def _try_load_model(
    paths: typing.Iterable[str | os.PathLike[typing.Any]] | None = None,
    environment: Environment | None = None,
    sysml_source: str | None = None,
    kerml_source: str | None = None,
    use_low_level_loading_api: bool = False,
) -> tuple[Model, Diagnostics]:
    validated_paths = _validate_parameters(paths, sysml_source, kerml_source)

    executor = get_default_executor()
    user_io_result = _create_user_documents(
        executor, validated_paths, sysml_source, kerml_source, use_low_level_loading_api
    )
    documents = _create_documents(user_io_result, syside.DocumentTier.Project)

    if environment is None:
        environment = Environment.get_default()
    index = environment.index()
    result = _build_model(executor, environment.lib, documents, index)

    model = Model(
        result,
        environment=environment,
        documents=documents,
        lib=environment.lib,
        index=index,
    )
    return model, _collect_diagnostics(result.documents, result.diagnostics)


@typing.overload
def try_load_model(
    paths: typing.Iterable[str | os.PathLike[typing.Any]],
    *,
    environment: Environment | None = None,
    sysml_source: str | None = None,
    kerml_source: str | None = None,
) -> tuple[Model, Diagnostics]: ...


@typing.overload
def try_load_model(
    paths: typing.Iterable[str | os.PathLike[typing.Any]],
    environment: Environment,
) -> tuple[Model, Diagnostics]: ...


@typing.overload
def try_load_model(
    *,
    sysml_source: str,
    kerml_source: str | None = ...,
    environment: Environment | None = None,
) -> tuple[Model, Diagnostics]: ...


@typing.overload
def try_load_model(
    *,
    kerml_source: str,
    sysml_source: str | None = ...,
    environment: Environment | None = None,
) -> tuple[Model, Diagnostics]: ...


def try_load_model(
    paths: typing.Iterable[str | os.PathLike[typing.Any]] | None = None,
    environment: Environment | None = None,
    sysml_source: str | None = None,
    kerml_source: str | None = None,
) -> tuple[Model, Diagnostics]:
    """Load a SysMLv2 model.

    At least one of ``paths``, ``sysml_source``, and ``kerml_source`` must not
    be none.

    :param paths:
        The paths to SysMLv2 or KerML files to load. These files must have
        correct file extensions (``.sysml`` or ``.kerml``).
    :param environment:
        The environment to be used for the model. If this parameter is left to
        ``None``, uses the default environment.
    :param sysml_source:
        A SysMLv2 source to be loaded as an in-memory file.
    :param kerml_source:
        A KerML source to be loaded as an in-memory file.
    :return:
        Model and Diagnostics pair. Note that models may only be partial if
        parsing failed, however even a partial model may be of interest for
        analysis.
    """

    return _try_load_model(paths, environment, sysml_source, kerml_source)


class ModelError(RuntimeError):
    """An exception thrown when model contains errors."""

    def __init__(self, model: Model, diagnostics: Diagnostics) -> None:
        super().__init__()

        self.model = model
        self.diagnostics = diagnostics

    def __str__(self) -> str:
        return str(self.diagnostics)


@typing.overload
def load_model(
    paths: typing.Iterable[str | os.PathLike[typing.Any]],
    *,
    environment: Environment | None = None,
    sysml_source: str | None = None,
    kerml_source: str | None = None,
    warnings_as_errors: bool = False,
) -> tuple[Model, Diagnostics]: ...


@typing.overload
def load_model(
    *,
    sysml_source: str,
    kerml_source: str | None = ...,
    environment: Environment | None = None,
    warnings_as_errors: bool = False,
) -> tuple[Model, Diagnostics]: ...


@typing.overload
def load_model(
    *,
    kerml_source: str,
    sysml_source: str | None = ...,
    environment: Environment | None = None,
    warnings_as_errors: bool = False,
) -> tuple[Model, Diagnostics]: ...


def load_model(
    paths: typing.Iterable[str | os.PathLike[typing.Any]] | None = None,
    environment: Environment | None = None,
    sysml_source: str | None = None,
    kerml_source: str | None = None,
    warnings_as_errors: bool = False,
) -> tuple[Model, Diagnostics]:
    """Load a SysMLv2 model.

    At least one of ``paths``, ``sysml_source``, and ``kerml_source`` must not
    be none.

    :param paths:
        The paths to SysMLv2 or KerML files to load. These files must have
        correct file extensions (``.sysml`` or ``.kerml``).
    :param environment:
        The environment to be used for the model. If this parameter is left to
        ``None``, uses the default environment. sysml_source: A SysMLv2 source
        to be loaded as an in-memory file. kerml_source: A KerML source to be
        loaded as an in-memory file.
    :return:
        Model and Diagnostics pair.
    :raises ModelError:
        If returned diagnostics contain errors, or if ``warnings_as_errors`` is
        ``True``, if diagnostics contain errors or warnings.
    """
    model, diags = _try_load_model(
        paths,
        environment=environment,
        sysml_source=sysml_source,
        kerml_source=kerml_source,
    )

    if diags.contains_errors(warnings_as_errors):
        raise ModelError(model, diags)

    return model, diags
