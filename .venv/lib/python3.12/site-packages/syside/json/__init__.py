"""
Convenience module intending to match the standard library ``json`` module.
"""

from collections.abc import Iterable
from typing import Callable, overload
import typing
from uuid import UUID
from warnings import warn
from dataclasses import dataclass

from .._loading import BaseModel, Environment
from .. import core as syside


@dataclass
class SerializationError(Exception):
    """
    Error serializing element to SysML v2 JSON.
    """

    report: syside.SerdeReport[syside.Element]


type DeserializationReport = syside.SerdeReport[
    syside.Element | str | syside.DocumentSegment
]


class SerdeError(Exception):
    """
    Class for exceptions from serialization and deserialization
    """


@dataclass
class DeserializationError(SerdeError):
    """
    Error deserializing document from SysML v2 JSON.
    """

    model: syside.DeserializedModel
    report: DeserializationReport

    def __str__(self) -> str:
        return str(self.report)


@dataclass
class ProjectDeserializationError(SerdeError):
    """
    Error deserializing project from SysML v2 JSON.
    """

    models: list[syside.DeserializedModel]
    reports: list[DeserializationReport]

    def __str__(self) -> str:
        return "\n".join(str(report) for report in self.reports)


class SerdeWarning(Warning):
    """
    Class for warnings from serialization and deserialization
    """


def dumps(
    element: syside.Element,
    options: syside.SerializationOptions,
    indent: int = 2,
    use_spaces: bool = True,
    final_new_line: bool = True,
    include_cross_ref_uris: bool = True,
) -> str:
    """
    Serialize ``element`` to a SysML v2 JSON ``str``.

    See the documentation of the :py:class:`SerializationOptions
    <syside.SerializationOptions>` class for documentation of the possible
    options. The options object constructed with
    :py:meth:`SerializationOptions.minimal
    <syside.SerializationOptions.minimal>` instructs to produce a minimal JSON
    without any redundant elements that results in significantly smaller JSONs.
    Examples of redundant information that is avoided using minimal
    configuration are:

    +   including fields for null values;
    +   including fields whose values match the default values;
    +   including redefined fields that are duplicates of redefining fields;
    +   including derived fields that can be computed from minimal JSON (for
        example, the result value of evaluating an expression);
    +   including implied relationships.

    .. note::

        Syside does not construct all derived properties yet. Therefore, setting
        ``options.include_derived`` to ``True`` may result in a JSON that does
        not satisfy the schema.

    :param element:
        The SysML v2 element to be serialized to SysML v2 JSON.
    :param options:
        The serialization options to use when serializing SysML v2 to JSON.
    :param indent:
        How many space or tab characters to use for indenting the JSON.
    :param use_spaces:
        Whether use spaces or tabs for indentation.
    :param final_new_line:
        Whether to add a newline character at the end of the generated string.
    :param include_cross_ref_uris:
        Whether to add potentially relative URIs as ``@uri`` property to
        references of Elements from documents other than the one owning
        ``element``. Note that while such references are non-standard, they
        match the behaviour of XMI exports in Pilot implementation which use
        relative URIs for references instead of plain element IDs.
    :return:
        ``element`` serialized as JSON.
    """

    writer = syside.JsonStringWriter(
        indent=indent,
        use_spaces=use_spaces,
        final_new_line=final_new_line,
        include_cross_ref_uris=include_cross_ref_uris,
    )

    report = syside.serialize(element, writer, options)

    if not report:
        raise SerializationError(report)

    for msg in report.messages:
        if msg.severity == syside.DiagnosticSeverity.Warning:
            warn(msg.message, category=SerdeWarning, stacklevel=2)

    return writer.result


type JsonSourceNew = tuple[str | syside.Url, str]
type JsonSourceInto = tuple[syside.Document, str]


def _deserialize_document(
    s: str,
    document: str | syside.Url | syside.Document,
    reader: syside.JsonReader,
    attributes: syside.AttributeMap | None = None,
) -> tuple[
    syside.DeserializedModel,
    DeserializationReport,
    syside.AttributeMap,
]:
    new_doc: syside.SharedMutex[syside.Document] | None = None
    if isinstance(document, str):
        document = syside.Url(document)
    if isinstance(document, syside.Url):
        ext = document.path.rsplit(".", 1)[-1].lower()
        if ext == "sysml":
            lang = syside.ModelLanguage.SysML
        elif ext == "kerml":
            lang = syside.ModelLanguage.KerML
        else:
            raise ValueError(f"Unknown document language, could not infer from '{ext}'")
        new_doc = syside.Document.create_st(url=document, language=lang)
        with new_doc.lock() as doc:
            document = doc  # appease pylint

    with reader.bind(s) as json:
        if attributes is None:
            attributes = json.attribute_hint()
        if attributes is None:
            raise ValueError("Cannot deserialize model with unmapped attributes")

        model, report = syside.deserialize(document, json, attributes)

    return model, report, attributes


_STDLIB_MAP: syside.IdMap | None = None


def _map_from_env(docs: Iterable[syside.SharedMutex[syside.Document]]) -> syside.IdMap:
    ids = syside.IdMap()
    for mutex in docs:
        with mutex.lock() as doc:
            ids.insert_or_assign(doc)
    return ids


def _loads_project(
    s: Iterable[JsonSourceNew | JsonSourceInto],
    environment: Environment | None = None,
    resolve: Callable[[str, UUID], syside.Element | None] | None = None,
    attributes: syside.AttributeMap | None = None,
) -> tuple[
    BaseModel,
    list[tuple[syside.DeserializedModel, DeserializationReport]],
]:
    reader = syside.JsonReader()

    init: list[tuple[syside.DeserializedModel, DeserializationReport]] = []
    for doc, src in s:
        model, report, attributes = _deserialize_document(src, doc, reader, attributes)
        init.append((model, report))

    passed = all(report.passed() for _, report in init)
    if not passed:
        raise ProjectDeserializationError(
            models=[model for model, _ in init], reports=[report for _, report in init]
        )

    for _, report in init:
        for msg in report.messages:
            if (
                msg.severity == syside.DiagnosticSeverity.Warning
                and not msg.message.startswith("Could not find reference")
            ):
                warn(msg.message, category=SerdeWarning, stacklevel=3)

    base: syside.IdMap | None = None
    if environment is None or environment is getattr(Environment, "_STDLIB", None):
        environment = Environment.get_default()
        # ignore pylint, we use global variable for caching
        global _STDLIB_MAP  # pylint: disable=global-statement
        if _STDLIB_MAP is None:
            _STDLIB_MAP = _map_from_env(environment.documents)
        base = _STDLIB_MAP
    elif not resolve:
        # defer environment map creation as it may be relatively expensive and
        # duplicate user provided ``resolve``
        base = _map_from_env(environment.documents)

    local: syside.IdMap | None = None
    if len(init) > 1:
        # small optimization as 1 document will have resolved its own references
        # automatically
        local = syside.IdMap()
        for model, _ in init:
            local.insert_or_assign(model.document)

    def resolver(url: str, uuid: UUID) -> syside.Element | None:
        if local and (result := local(url, uuid)):
            return result

        if resolve and (result := resolve(url, uuid)):
            return result

        nonlocal base
        if base is None:
            base = _map_from_env(environment.documents)

        if result := base(url, uuid):
            return result

        return None

    index = environment.index()
    for i, (model, _) in enumerate(init):
        init[i] = (model, model.link(resolver)[0])
        syside.collect_exports(model.document)
        index.insert(model.document)

    passed = all(report.passed() for _, report in init)
    if not passed:
        raise ProjectDeserializationError(
            models=[model for model, _ in init], reports=[report for _, report in init]
        )

    return BaseModel(
        result=None,
        environment=environment,
        documents=[model.document.mutex for model, _ in init],
        lib=environment.lib,
        index=index,
    ), init


def _loads_document(
    s: str,
    document: syside.Document | syside.Url | str,
    attributes: syside.AttributeMap | None = None,
) -> (
    syside.DeserializedModel
    | tuple[syside.DeserializedModel, syside.SharedMutex[syside.Document]]
):
    reader = syside.JsonReader()

    model, report, _ = _deserialize_document(s, document, reader, attributes)

    if not report:
        raise DeserializationError(model, report)

    for msg in report.messages:
        if msg.severity == syside.DiagnosticSeverity.Warning:
            warn(msg.message, category=SerdeWarning, stacklevel=3)

    if not isinstance(document, syside.Document):
        return model, model.document.mutex
    return model


@overload
def loads(
    s: str,
    document: syside.Document,
    attributes: syside.AttributeMap | None = None,
) -> syside.DeserializedModel:
    """
    Deserialize a model from ``s`` into an already existing ``document``.

    Root node will be inferred as:

    1. The first ``Namespace`` (not subtype) without an owning relationship.
    2. The first ``Element`` that has no serialized owning related element or owning relationship,
       starting from the first element in the JSON array, and following owning elements up.
    3. The first element in the array otherwise.

    :param s:
        The string contained serialized SysML model in JSON array.
    :param document:
        The document the model will be deserialized into.
    :param attributes:
        Attribute mapping of ``s``. If none provided, this will attempt to infer
        a corresponding mapping or raise a ``ValueError``.
    :return:
        Model deserialized from JSON array. Note that references into other
        documents will not be resolved, users will need to resolve them by
        calling ``link`` on the returned model. See also :py:class:`IdMap
        <syside.IdMap>`.
    """


@overload
def loads(
    s: str,
    document: syside.Url | str,
    attributes: syside.AttributeMap | None = None,
) -> tuple[syside.DeserializedModel, syside.SharedMutex[syside.Document]]:
    """
    Create a new ``document`` and deserialize a model from ``s`` into it.

    Root node will be inferred as:

    1. The first ``Namespace`` (not subtype) without an owning relationship.
    2. The first ``Element`` that has no serialized owning related element or owning relationship,
       starting from the first element in the JSON array, and following owning elements up.
    3. The first element in the array otherwise.

    :param s:
        The string contained serialized SysML model in JSON array.
    :param document:
        A URI in the form of :py:class:`Url <syside.Url>` or a string, new
        document will be created with. If URI path has no extension, or the
        extension does not match ``sysml`` or ``kerml``, ``ValueError`` is
        raised.
    :param attributes:
        Attribute mapping of ``s``. If none provided, this will attempt to infer
        a corresponding mapping or raise a ``ValueError``.
    :return:
        Model deserialized from JSON array and the newly created document. Note that
        references into other documents will not be resolved, users will need to
        resolve them by calling ``link`` on the returned model. See also
        :py:class:`IdMap <syside.IdMap>`.
    """


@overload
def loads(
    s: Iterable[JsonSourceNew | JsonSourceInto],
    /,
    environment: Environment | None = None,
    resolve: Callable[[str, UUID], syside.Element | None] | None = None,
    attributes: syside.AttributeMap | None = None,
) -> tuple[
    BaseModel,
    list[tuple[syside.DeserializedModel, DeserializationReport]],
]:
    """
    Deserialize a project of multiple documents from ``s``.

    This is effectively calling ``loads(src, document, attributes) for document,
    src in s`` and performing the link step afterwards. See also other overloads
    of ``loads``.

    :param s:
        Projects sources to deserialize from. If providing a URL string or a
        ``Url``, new documents will be created for corresponding sources,
        otherwise deserialization will be performed into the provided
        ``Documents``.
    :param environment:
        ``Environment`` this project depends on. Defaults to the bundled
        standard library. The ``environment`` will be used to attempt to resolve
        missing references in the deserialized project.
    :param resolve:
        User-provided reference resolution callback that takes priority over
        ``environment``. See :py:meth:`DeserializedModel.link
        <syside.DeserializedModel.link>` for more details.
    :param attributes:
        Attribute mapping of ``s``. If none provided, this will attempt to infer
        a corresponding mapping or raise a ``ValueError``.
    :return:
        A tuple of project deserialized from JSON sources, and deserialization
        results
    :raises ProjectDeserializationError:
        If either the deserialization or the reference resolution had errors.
    """


def loads(
    s: str | Iterable[JsonSourceNew | JsonSourceInto],
    *args: typing.Any,
    **kwargs: typing.Any,
) -> (
    syside.DeserializedModel
    | tuple[syside.DeserializedModel, syside.SharedMutex[syside.Document]]
    | tuple[
        BaseModel,
        list[tuple[syside.DeserializedModel, DeserializationReport]],
    ]
):
    """loads implementation"""
    if isinstance(s, str):
        return _loads_document(s, *args, **kwargs)
    return _loads_project(s, *args, **kwargs)
