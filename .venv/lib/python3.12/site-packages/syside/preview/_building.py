"""
Upcoming module implementing proposals for how to make adding model elements easier.
"""

import typing

from .. import core as syside


_VISIBILITY_KIND: typing.Dict[
    typing.Optional[str | syside.VisibilityKind], typing.Optional[syside.VisibilityKind]
] = {
    None: None,
    "private": syside.VisibilityKind.Private,
    "protected": syside.VisibilityKind.Protected,
    "public": syside.VisibilityKind.Public,
    syside.VisibilityKind.Private: syside.VisibilityKind.Private,
    syside.VisibilityKind.Protected: syside.VisibilityKind.Protected,
    syside.VisibilityKind.Public: syside.VisibilityKind.Public,
}

ElementKind = typing.TypeVar("ElementKind", bound=syside.Element)
## For now a single type
OwnershipKind = syside.OwningMembership


def _visibility_kind_new_element(
    visibility: typing.Optional[syside.VisibilityKind],
    kind: type[ElementKind],
    ownership_kind: type[OwnershipKind],
    owner: syside.Namespace,
    name: typing.Optional[str],
    short_name: typing.Optional[str],
) -> ElementKind:
    ownership, element = owner.children.append(ownership_kind, kind)

    if name is not None:
        element.declared_name = name

    if short_name is not None:
        element.declared_short_name = short_name

    if visibility is not None:
        ownership.visibility = visibility

    return element


def new_package(
    owner: syside.Namespace,
    name: typing.Optional[str] = None,
    short_name: typing.Optional[str] = None,
    *,
    visibility: typing.Optional[
        typing.Literal["private", "protected", "public"] | syside.VisibilityKind
    ] = None,
) -> syside.Package:
    """
    Adds a new package (Section 7.5)
    """
    return _visibility_kind_new_element(
        visibility=_VISIBILITY_KIND[visibility],
        kind=syside.Package,
        ownership_kind=syside.OwningMembership,
        owner=owner,
        name=name,
        short_name=short_name,
    )


def new_library_package(
    owner: syside.Namespace,
    name: typing.Optional[str] = None,
    short_name: typing.Optional[str] = None,
    *,
    visibility: typing.Optional[
        typing.Literal["private", "protected", "public"] | syside.VisibilityKind
    ] = None,
) -> syside.LibraryPackage:
    """
    Adds a new package (Section 7.5)
    """
    return _visibility_kind_new_element(
        visibility=_VISIBILITY_KIND[visibility],
        kind=syside.LibraryPackage,
        ownership_kind=syside.OwningMembership,
        owner=owner,
        name=name,
        short_name=short_name,
    )
