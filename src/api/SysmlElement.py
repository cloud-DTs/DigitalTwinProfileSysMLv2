from dataclasses import dataclass
from enum import Enum

class Field(Enum):
    ID = "@id"
    TYPE = "@type"
    NAME = "name"
    OWNED_FEATURE = "ownedFeature"
    INHERITED_FEATURE = "inheritedFeature"
    OWNED_SUBSETTING = "ownedSubsetting"
    OWNED_REDEFINITION = "ownedRedefinition"
    MEMBER = "member"
    MEMBERSHIP = "membership"
    MEMBER_ELEMENT = "memberElement"
    CHAINING_FEATURE = "chainingFeature"
    REFERENT = "referent"
    VALUE = "value"
    MULTIPLICITY = "multiplicity"
    METADATA_DEFINITION = "metadataDefinition"
    ANNOTATED_ELEMENT = "annotatedElement"
    SUBSETTED_FEATURE = "subsettedFeature"
    REDEFINED_FEATURE = "redefinedFeature"

class SysmlType:
    METADATA_DEFINITION = "MetadataDefinition"
    METADATA_USAGE = "MetadataUsage"
    OWNING_MEMBERSHIP = "OwningMembership"
    FEATURE_REFERENCE_EXPRESSION = "FeatureReferenceExpression"
    FEATURE_CHAIN_EXPRESSION = "FeatureChainExpression"
    LITERAL_STRING = "LiteralString"
    LITERAL_INTEGER = "LiteralInteger"
    LITERAL_BOOLEAN = "LiteralBoolean"
    LITERAL_RATIONAL = "LiteralRational"
    

@dataclass
class SysmlElement:
    id: str
    name: str
    type: SysmlType
    raw: dict

    def getField(self, field: Field):
        return self.raw.get(field.value, None)
    
    @staticmethod
    def parseRaw(raw: dict) -> 'SysmlElement':
        element = raw.get("payload", raw)
        id = element.get(Field.ID.value, None)
        name = element.get(Field.NAME.value, None)
        type = element.get(Field.TYPE.value, None)
        raw = element
        return SysmlElement(id=id, name=name, type=type, raw=element)

    