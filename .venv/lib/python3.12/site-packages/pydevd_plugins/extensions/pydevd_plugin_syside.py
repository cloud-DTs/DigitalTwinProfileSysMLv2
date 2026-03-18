from __future__ import annotations

import typing

if not typing.TYPE_CHECKING:
    from _pydevd_bundle.pydevd_extension_api import (  # type: ignore
        TypeResolveProvider,
        StrPresentationProvider,
    )
else:
    import syside

    class TypeResolveProvider:
        @classmethod
        def register(cls, t: type) -> None: ...

    class StrPresentationProvider:
        @classmethod
        def register(cls, t: type) -> None: ...


def _provide(cls: type, base: type, t: str | tuple[str, ...]):
    class Wrapper(cls, base):
        def can_provide(self, type_object: type, type_name: str) -> bool:
            import syside

            if not isinstance(t, str):
                types = tuple(getattr(syside, name) for name in t)
            else:
                types = (getattr(syside, t),)

            return issubclass(type_object, types)

    return Wrapper


def type_provider(t: str | tuple[str, ...]):
    def wrapper[T](cls: type[T]) -> type[T]:
        TypeResolveProvider.register(cls)
        return _provide(cls, TypeResolveProvider, t)

    return wrapper


def str_provider(t: str | tuple[str, ...]):
    def wrapper[T](cls: type[T]) -> type[T]:
        StrPresentationProvider.register(cls)
        return _provide(cls, StrPresentationProvider, t)

    return wrapper


@type_provider("LazyIterator")
class LazyIteratorResolver:
    def get_dictionary(self, var: syside.LazyIterator):
        items = var.collect()
        return {str(i): item for i, item in enumerate(items)}

    def resolve(self, var, attribute):
        return var.at(int(attribute))


@str_provider("LazyIterator")
class LazyIteratorStr(StrPresentationProvider):
    def get_str(self, val: syside.LazyIterator) -> str:
        return f"LazyIterator( empty = {val.empty()} )"


@type_provider("ChildrenNodesView")
class ChildrenNodesResolver(TypeResolveProvider):
    def get_dictionary(self, var: syside.ChildrenNodesView):
        values: dict[str, typing.Any] = {
            str(i): item for i, item in enumerate(zip(var.relationships, var.elements))
        }
        values["relationships"] = var.relationships
        values["elements"] = var.elements
        return values

    def resolve(self, var, attribute):
        try:
            return var[int(attribute)]
        except TypeError:
            return getattr(var, attribute)


@str_provider("ChildrenNodesView")
class ChildrenNodesStr(StrPresentationProvider):
    def get_str(self, val: syside.ChildrenNodesView) -> str:
        return f"ChildrenNodes( len = {len(val)} )"


@type_provider("ContainerView")
class ContainerResolver(TypeResolveProvider):
    def get_dictionary(self, var: syside.ContainerView):
        return {str(i): item for i, item in enumerate(var)}

    def resolve(self, var, attribute):
        return var[int(attribute)]


@str_provider("ContainerView")
class ContainerStr(StrPresentationProvider):
    def get_str(self, val: syside.ContainerView) -> str:
        return f"ContainerView( len = {len(val)} )"


OBJECTS = (
    "AstNode",
    "BasicDocument",
    "MemberAccessor",
    "ReferenceAccessor",
)


@type_provider(OBJECTS)
class ObjectResolver(TypeResolveProvider):
    def get_dictionary(self, var):
        out = {}
        for name in dir(var):
            if name.startswith("_"):
                continue
            value = getattr(var, name)

            # ignore nanobind methods
            if type(value).__module__ != "nanobind":
                out[name] = value
        return out

    def resolve(self, var, attribute):
        return getattr(var, attribute)


@str_provider("AstNode")
class NodeStr(StrPresentationProvider):
    def get_str(self, val: syside.AstNode) -> str:
        return f"{val.__class__.__name__} `{val}`"


@str_provider("BasicDocument")
class DocumentStr(StrPresentationProvider):
    def get_str(self, val: syside.BasicDocument) -> str:
        return f"{val.language} {val.__class__.__name__} `{val.url}`"


@str_provider("MemberAccessor")
class MemberAccessorStr(StrPresentationProvider):
    def get_str(self, val: syside.MemberAccessor) -> str:
        target = val.member_element
        if target:
            return f"MemberAccessor( {target.__class__.__name__} `{target}` )"
        return "MemberAccessor( None )"


@str_provider("ReferenceAccessor")
class ReferenceAccessorStr(StrPresentationProvider):
    def get_str(self, val: syside.ReferenceAccessor) -> str:
        target = val.element
        if target is None:
            return "ReferenceAccessor( None )"
        return f"ReferenceAccessor( {target.__class__.__name__} `{target}` )"
