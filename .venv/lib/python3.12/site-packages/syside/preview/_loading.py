"""
Module implementing proposals for how to make loading and locking
models and documents easier.
"""

from pathlib import Path
import urllib.parse
import typing
from types import TracebackType
from contextlib import ExitStack
from bisect import insort
from threading import RLock
import sys


from .. import core as syside
from .. import _loading as syside_loading
from .. import _diagnostics as syside_diagnostics
from . import _building as syside_building

# pylint: disable=no-member, protected-access
if hasattr(sys, "_is_gil_enabled") and not sys._is_gil_enabled():
    _new_document = syside.Document.create_mt
else:
    _new_document = syside.Document.create_st


def _get_unlocked_document_hash(
    document: syside.SharedMutex[syside.Document],
) -> int:
    with document.lock() as locked_document:
        return hash(locked_document)


def _lookup_namespace_ambiguous(
    namespace: syside.Namespace, name: str
) -> typing.Iterator[syside.Element]:
    for _, element in iter(namespace.children):
        if name in [element.name, element.short_name]:
            yield element


def _lookup_namespace(
    namespace: syside.Namespace, name: str, *path: str
) -> syside.Element | None:
    elements = _lookup_namespace_ambiguous(namespace, name)

    candidate = next(elements, None)

    if next(elements, None) is not None:
        raise NameError(f"ambiguous name {namespace}::'{name}'")

    match path:
        case ():
            return candidate
        case (new_name, *new_path):
            if isinstance(candidate, syside.Namespace):
                return _lookup_namespace(candidate, new_name, *new_path)

            raise TypeError(f"{namespace}::'{name}' is not a Namespace")

    raise RuntimeError("Unreachable")


class UnlockedModel:
    """
    A SysML v2/KerML model that needs to be ``lock``\\ed before access.

    Note that ``UnlockedModel`` is generally not intended to be instantiated directly. Ideally,
    use ``open_model_unlocked`` or ``LockedModel.unlock`` on a previously acquired ``LockedModel``.

    .. code:: python

       model : UnlockedModel = open_model_unlocked("file.sysml")

       ## Alternatively
       locked_model : LockedModel = open_model("file.sysml")
       ...
       model = locked_model.unlock()
    """

    _global_lock = RLock()

    def __init__(
        self,
        documents: typing.Iterable[syside.SharedMutex[syside.Document]],
        diagnostics: syside_diagnostics.Diagnostics,
    ):
        """
        :param documents:
            sequence of ``syside.Document``\\s that constitute the model

        :param diagnostics:
            any diagnostic messages (errors or warnings) concerning the model
        """
        self.diagnostics = diagnostics

        # Avoid deadlocks by using a global locking order
        self._documents = sorted(
            (
                (_get_unlocked_document_hash(document), document)
                for document in documents
            ),
            key=lambda x: x[0],
        )

    def lock(self) -> "LockedModel":
        """
        Locks the model, allowing access.

        :return:
            a ``LockedModel`` that allows access to model elements.
        """
        locked_model = LockedModel()
        return locked_model._lock(self)


class LockedModel:
    """
    A SysML v2/KerML model interface. Top level elements (typically Packages) can be accessed
    through the ``lookup`` method, e.g. ``model.lookup("PackageName")``. To create a new top level
    package use the ``new_top_level_package`` method.

    The object is invalidated once ``unlock``\\ed, either explicitly or by leaving the outermost
    ``with``\\-block when used as a context manager.

    Note that ``LockedModel`` is generally not intended to be instantiated directly. Ideally,
    use either ``open_model`` or ``empty_model``. Alternatively, instantiate ``UnlockedModel``
    and use ``UnlockedModel.lock``.

    .. code:: python

       model : LockedModel = empty_model()

       ## Alternatively
       unlocked_model = open_model_unlocked(...)

       model : LockedModel = unlocked_model.lock()
    """

    ## NOTE: Constructor *does not* lock and is generally not intended to be used by users
    ## Type annotation to make mypy happy
    def __init__(self: "LockedModel"):
        # Equivalent to self._invalidate()
        self._model: UnlockedModel | None = None
        self._exit_stack: ExitStack | None = None
        self._locked_documents: typing.List[syside.Document] | None = None

        ## Depth of context manager nestings
        self._nesting = 0

    def _invalidate(self) -> None:
        self._model = None
        self._exit_stack = None
        self._locked_documents = None

    def _lock(self, model: UnlockedModel) -> "LockedModel":
        # pylint: disable-next=consider-using-with
        UnlockedModel._global_lock.acquire()

        self._model = model

        self._exit_stack = ExitStack()
        # pylint: disable-next=unnecessary-dunder-call
        self._exit_stack.__enter__()

        self._locked_documents = [
            self._exit_stack.enter_context(doc.lock())
            for name, doc in self._model._documents
        ]

        return self

    def __enter__(self) -> typing.Self:
        if self._exit_stack is None:
            raise RuntimeError("Invalid LockedModel, probably used after unlocking")

        self._nesting += 1

        return self

    def _unlock(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> tuple[bool | None, UnlockedModel]:
        if self._exit_stack is None or self._model is None:
            raise RuntimeError("Invalid LockedModel, probably used after unlocking")

        model = self._model
        cm_ret = self._exit_stack.__exit__(exc_type, exc_value, traceback)

        self._invalidate()

        UnlockedModel._global_lock.release()

        return (cm_ret, model)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        if self._exit_stack is None:
            return False

        self._nesting -= 1

        # Leaving the outermost CM
        if not self._nesting:
            return self._unlock(exc_type, exc_value, traceback)[0]

        return False

    def unlock(self) -> UnlockedModel:
        """
        Unlocks the model, freeing it up for others to lock.

        :return:
            ``UnlockedModel`` that can be used to re-acquire access to the model

        :raises RuntimeError: if used after unlocking
        """
        return self._unlock(None, None, None)[1]

    @property
    def diagnostics(self) -> syside_diagnostics.Diagnostics:
        """
        Diagnostics generated when the model was loaded.
        """
        if self._model is None:
            raise RuntimeError("Invalid LockedModel, probably used after unlocking")

        return self._model.diagnostics

    ## Various functions to make it behave like a dict[str,Element]
    def top_elements(self) -> typing.Iterator[syside.Element]:
        """
        Yields all top level named elements (typically Packages) that are owned
        members of a root namespace in the model. Note that imported members are
        not taken into account.

        :return:
            sequence of top level elements

        :raises RuntimeError: if used after unlocking
        """
        # Is unlocked
        if self._locked_documents is None:
            raise RuntimeError("Invalid LockedModel, probably used after unlocking")

        for locked_document in self._locked_documents:
            for _, element in iter(locked_document.root_node.children):
                yield element

    def top_named_elements(self) -> typing.Iterator[tuple[str, syside.Element]]:
        """
        Yields all named top level named elements (typically Packages) that are owned
        members of a root namespace in the model, together with (one of) their names.
        Note that imported members are
        not taken into account.

        Prefers name over short name.

        :return:
            sequence of (name, element) pairs of named top level elements

        :raises RuntimeError: if used after unlocking
        """
        for element in self.top_elements():
            preferred_name = element.name or element.short_name
            if preferred_name is not None:
                yield (preferred_name, element)

    def top_names(self) -> typing.Iterator[str]:
        """
        Yields names of all top level named elements (typically Packages) that are owned
        members of a root namespace in the model. Note that imported members are
        not taken into account.

        Prefers name over short name.

        :return:
            sequence of names of named top level elements

        :raises RuntimeError: if used after unlocking
        """
        for element in self.top_elements():
            preferred_name = element.name or element.short_name
            if preferred_name is not None:
                yield preferred_name

    def _lookup_ambiguous(self, name: str) -> typing.Iterator[syside.Element]:
        return (
            element
            for element in self.top_elements()
            if name in [element.name, element.short_name]
        )

    def lookup(self, name: str, *path: str) -> syside.Element | None:
        """
        If ``path`` is empty, yields the (unique) top-level owned member element with name
        ``name`` if it exists, otherwise returns ``None``. Note that elements other than
        owned member elements, such as imported or inherited ones, are not taken into account.

        Otherwise ``.lookup(name, name, path1, ..., pathn)`` is equal to
        ``.lookup(name).lookup(path1).[...].lookup(pathn)``, unless any intermediate value
        is ``None``. If any intermediate value is ``None`` the whole expression evaluates to
        ``None``.

        :param name:
            name of element to find

        :param path:
            sequence of names to (recursively) lookup

        :return:
            (unique) element with name ``name`` or None (if not found)

        :raises RuntimeError: if used after unlocking

        :raises TypeError: if trying to recursively look-up into a non-``Namespace`` element.

        :raises NameError: if the name is ambiguous.
        """
        elements = self._lookup_ambiguous(name)

        candidate = next(elements, None)

        if next(elements, None) is not None:
            raise NameError(f"ambiguous name '{name}'")

        match path:
            case ():
                return candidate
            case (new_name, *new_path):
                if isinstance(candidate, syside.Namespace):
                    return _lookup_namespace(candidate, new_name, *new_path)

                raise TypeError(f"'{name}' is not a Namespace")

        raise RuntimeError("Unreachable")

    ## Entrypoint(s) for future updated editor integration API
    def top_elements_from(self, path: str | Path) -> typing.Iterator[syside.Element]:
        """
        Yields top level owned member elements (typically Packages) loaded from the specified
        path(or from files below that path if it is a directory). Note that imported members are
        not taken into account.

        :param path:
            source file or directory path to return elements loaded from

        :return:
            sequence of (top) model elements loaded from source file(s)
            matching ``path``

        :raises RuntimeError: if used after unlocking
        """
        if self._locked_documents is None:
            raise RuntimeError("Invalid LockedModel, probably used after unlocking")

        path = Path(path).resolve()
        for locked_document in self._locked_documents:
            # We do not deal with remote/memory files right now
            if locked_document.url.has_scheme and locked_document.url.scheme != "file":
                continue
            document_path = Path(syside.decode_path(locked_document.url))

            if path == document_path or (
                path.is_dir() and path in document_path.parents
            ):
                yield from (
                    element for _, element in iter(locked_document.root_node.children)
                )

    ## Entrypoint(s) for future updated model building API
    def _new_model_document(self, name_hint: str) -> syside.Document:
        # Is unlocked
        if (
            self._exit_stack is None
            or self._locked_documents is None
            or self._model is None
        ):
            raise RuntimeError("Trying to add package to unlocked model")

        doc_url = syside.Url(f"memory://{urllib.parse.quote(name_hint, safe='')}.sysml")

        doc = _new_document(syside.DocumentOptions(url=doc_url, language="sysml"))

        insort(
            self._model._documents,
            (_get_unlocked_document_hash(doc), doc),
            key=lambda x: x[0],
        )

        locked_doc = self._exit_stack.enter_context(doc.lock())
        self._locked_documents.append(locked_doc)

        return locked_doc

    def new_top_level_package(self, name: str) -> syside.Package:
        """
        Creates a (named) new top level package.

        :param name:
            name of the new package

        :return:
            a new ``syside.Package`` named ``name`` (in a new global namespace)

        :raises RuntimeError: if used after unlocking
        """
        return syside_building.new_package(
            self._new_model_document(name).root_node, name=name
        )

    def new_top_level_library_package(self, name: str) -> syside.LibraryPackage:
        """
        Creates a (named) new top level package.

        :param name:
            name of the new package

        :return:
            a new ``syside.LibraryPackage`` named ``name`` (in a new global namespace)

        :raises RuntimeError: if used after unlocking
        """
        return syside_building.new_library_package(
            self._new_model_document(name).root_node, name=name
        )


def open_model_unlocked(
    paths: Path | str | typing.Iterable[Path | str],
    *,
    warnings_as_errors: bool = False,
    allow_errors: bool = False,
    include_stdlib: bool = True,
    environment: syside_loading.Environment | None = None,
) -> UnlockedModel:
    """
    Opens a model stored in ``paths``, which can be given as a (combination of) file and directory
    paths. By default the model is allowed to generate warnings (``warnings_as_errors``) but is not
    allowed to contain errors (``allow_errors``).

    ``lock`` the returned model before access

    :param paths:
        path or sequence of paths (given as ``str`` or ``Path``) of source files, or directories
        containing source files, to be included in the model
    :param warnings_as_errors:
        if True, warnings are treated errors
    :param allow_errors:
        if True, tries to return a partial or invalid model even in the presence of errors
    :param include_stdlib:
        if False, tries to load the model without also loading the SysML v2 standard library
    :param environment:
        The environment to be used for the model. If this parameter is ``None``, the default
        environment is used.

    :return:
        an ``UnlockedModel`` representing the model loaded from source files given in ``paths``

    :raises syside.ModelError: if model contains errors and ``allow_errors`` is False
    """

    def actual_absolute_paths() -> typing.Iterator[Path]:
        if isinstance(paths, (Path, str)):
            yield Path(paths).absolute()
        else:
            for path in paths:
                yield Path(path).absolute()

    def actual_source_file_paths() -> typing.Iterator[Path]:
        for path in actual_absolute_paths():
            if path.is_dir():
                yield from syside_loading.collect_files_recursively(path)
            else:
                yield path

    model, diagnostics = syside_loading.try_load_model(
        actual_source_file_paths(), environment=environment
    )

    if not allow_errors and diagnostics.contains_errors(warnings_as_errors):
        raise syside_loading.ModelError(model, diagnostics)

    return UnlockedModel(
        documents=model.all_docs if include_stdlib else model.user_docs,
        diagnostics=diagnostics,
    )


def open_model(
    paths: Path | str | typing.Iterable[Path | str],
    *,
    warnings_as_errors: bool = False,
    allow_errors: bool = False,
    include_stdlib: bool = True,
    environment: syside_loading.Environment | None = None,
) -> LockedModel:
    """
    Opens a model stored in ``paths``, which can be given as a (combination of) file and directory
    paths. By default the model is allowed to generate warnings (``warnings_as_errors``) but is not
    allowed to contain errors (``allow_errors``).

    ``unlock`` the returned model before sharing between threads (and re-lock before use), or use a
    ``with``\\-block to automatically unlock when exiting the block.

    :param paths:
        path or sequence of paths (given as ``str`` or ``Path``) of source files, or directories
        containing source files, to be included in the model
    :param warnings_as_errors:
        if True, warnings are treated errors
    :param allow_errors:
        if True, tries to return a partial or invalid model even in the presence of errors
    :param include_stdlib:
        if False, tries to load the model without also loading the SysML v2 standard library
    :param environment:
        The environment to be used for the model. If this parameter is ``None``, the default
        environment is used.

    :return:
        a ``LockableModel`` representing the model loaded from source files given in ``paths``

    :raises syside.ModelError: if model contains errors and ``allow_errors`` is False
    """

    return open_model_unlocked(
        paths=paths,
        warnings_as_errors=warnings_as_errors,
        allow_errors=allow_errors,
        include_stdlib=include_stdlib,
        environment=environment,
    ).lock()


def empty_model(
    *,
    warnings_as_errors: bool = False,
    allow_errors: bool = False,
    include_stdlib: bool = True,
    environment: syside_loading.Environment | None = None,
) -> LockedModel:
    """
    Opens an empty model, loading only standard library elements (unless ``include_stdlib=False``).

    ``unlock`` the returned model before sharing between threads (and re-lock before use), or use a
    ``with``-block to automatically unlock when exiting the block.

    :param warnings_as_errors:
        if True, warnings are treated errors
    :param allow_errors:
        if True, tries to return a partial or invalid model even in the presence of errors
    :param include_stdlib:
        if False, tries to load the model without also loading the SysML v2 standard library
    :param environment:
        The environment to be used for the model. If this parameter is ``None``, the default
        environment is used.

    :return:
        a ``LockableModel`` representing an empty model.
    """

    return open_model(
        paths=(),
        warnings_as_errors=warnings_as_errors,
        allow_errors=allow_errors,
        include_stdlib=include_stdlib,
        environment=environment,
    )
