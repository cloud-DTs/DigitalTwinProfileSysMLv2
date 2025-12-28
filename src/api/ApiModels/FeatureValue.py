from sysml_v2_api_client import Element as ElementOrigin
from .CommonElement import CommonElement
from .Element import Element
class FeatureValue(Element,ElementOrigin):
    openapi_types = {**Element.openapi_types, **ElementOrigin.openapi_types}
    openapi_types['value'] = 'str'
    openapi_types['referent'] = 'str'
    attribute_map = {**Element.attribute_map, **ElementOrigin.attribute_map}
    attribute_map['value'] = 'value'
    attribute_map['referent'] = 'referent'
  
    
    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, value):
        self._value = value
    def __init__(self):
        Element.__init__(self)
        ElementOrigin.__init__(self)
        self._value = None
    
    @property
    def referent(self):
        return self._referent
    @referent.setter
    def referent(self, referent):
        self._referent = referent
    def get_referent(self) -> Element|None:
        from ..element import getElementById
        if self.referent:
            referent_element = getElementById(self.referent)
            if referent_element:
                return referent_element
        return None
    