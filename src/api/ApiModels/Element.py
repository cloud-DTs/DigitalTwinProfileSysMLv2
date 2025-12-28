from __future__ import annotations
from sysml_v2_api_client import Element as ElementOrigin
from .CommonElement import CommonElement
class Element(CommonElement,ElementOrigin):
    openapi_types = {**CommonElement.openapi_types, **ElementOrigin.openapi_types}
    openapi_types['name'] = 'str'
    openapi_types['owner'] = 'dict[str, str]'
    openapi_types ['ownedFeature'] = 'list[dict[str, str]]'
    openapi_types ['inheritedFeature'] = 'list[dict[str, str]]'
    openapi_types ['ownedRedefinition'] = 'list[dict[str, str]]'
    openapi_types ['member'] = 'list[dict[str, str]]'
    openapi_types ['membership'] = 'list[dict[str, str]]'
    openapi_types['memberElement'] = 'dict[str, str]'
    openapi_types['chainingFeature'] = 'list[dict[str, str]]'
    openapi_types['value'] = 'str'
    openapi_types['referent'] = 'str'
    attribute_map = {**CommonElement.attribute_map, **ElementOrigin.attribute_map}
    attribute_map['name'] = 'name'
    attribute_map['owner'] = 'owner'
    attribute_map['ownedFeature'] = 'ownedFeature'
    attribute_map['inheritedFeature'] = 'inheritedFeature'
    attribute_map['ownedRedefinition'] = 'ownedRedefinition'
    attribute_map['member'] = 'member'
    attribute_map['membership'] = 'membership'
    attribute_map['memberElement'] = 'memberElement'
    attribute_map['chainingFeature'] = 'chainingFeature'
    attribute_map['value'] = 'value'
    attribute_map['referent'] = 'referent'


    def __init__(self):
        super().__init__()
        self._name = None
        self._owner = None
        self._ownedFeature = None
        self._inheritedFeature = None
        self._ownedRedefinition = None
        self._member = None
        self._identifier = None
        self.isIneherited = False
        self._membership = None
        self._memberElement = None
        self._chainingFeature = None
        self._value = None
        self._referent = None

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        self._name = value

    @property
    def owner(self):
        return self._owner
    @owner.setter
    def owner(self, value):
        self._owner = value
    @property
    def ownedFeature(self):
        return self._ownedFeature
    @ownedFeature.setter
    def ownedFeature(self, value):
        self._ownedFeature = value
    @property
    def inheritedFeature(self):
        return self._inheritedFeature
    @inheritedFeature.setter
    def inheritedFeature(self, value):
        self._inheritedFeature = value

    @property
    def ownedRedefinition(self):
        return self._ownedRedefinition
    @ownedRedefinition.setter
    def ownedRedefinition(self, value):
        self._ownedRedefinition = value
    @property
    def member(self):
        return self._member
    @member.setter
    def member(self, value):
        self._member = value
    
    @property
    def identifier(self):
        return self._identifier
    @identifier.setter
    def identifier(self, value):
        self._identifier = value
    
    @property
    def membership(self):
        return self._membership
    @membership.setter
    def membership(self, value):
        self._membership = value

    @property
    def memberElement(self):
        return self._memberElement
    @memberElement.setter
    def memberElement(self, value):
        self._memberElement = value

    @property
    def chainingFeature(self):
        return self._chainingFeature
    @chainingFeature.setter
    def chainingFeature(self, value):
        self._chainingFeature = value

    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, value):
        self._value = value
    @property
    def referent(self):
        return self._referent
    @referent.setter
    def referent(self, referent):
        self._referent = referent

    def get_member_ship(self) -> list['Element']:
        from ..element import getElementById
        members = []
        if self.membership:
            for mem in self.membership:
                member_id = mem.get('id')
                if member_id:
                    member_element = getElementById(member_id)
                    if member_element:
                        members.append(member_element)
        return members
    
    def get_owned_features(self) -> list['Element']:
        from ..element import getElementById
        features = []
        if self.ownedFeature:
            for feat in self.ownedFeature:
                feature_id = feat.get('id')
                if feature_id:
                    feature_element = getElementById(feature_id)
                    if feature_element:
                        features.append(feature_element)
        return features
    def get_inherited_features(self) -> list['Element']:
        from ..element import getElementById
        features = []
        if self.inheritedFeature:
            for feat in self.inheritedFeature:
                feature_id = feat.get('id')
                if feature_id:
                    feature_element = getElementById(feature_id)
                    if feature_element:
                        features.append(feature_element)
        return features
    
    def get_all_sub_features(self) -> list['Element']:
        
        all_features = self.get_owned_features()
        if self.isIneherited:
            inherited = self.get_inherited_features()
            all_features.extend(inherited)
        return all_features

    def get_member_element(self) -> Element|None:
        from ..element import getElementById
        if self.memberElement:
            member_id = self.memberElement.get('@id',None)
            if member_id:
                member_element = getElementById(member_id)
                return member_element
        return None

    