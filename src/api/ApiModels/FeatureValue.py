from sysml_v2_api_client import Element as ElementOrigin
from .CommonElement import CommonElement
from .Element import Element
class FeatureValue(Element,ElementOrigin):
    openapi_types = {**Element.openapi_types, **ElementOrigin.openapi_types}
    openapi_types['value'] = 'str'
    attribute_map = {**Element.attribute_map, **ElementOrigin.attribute_map}
    attribute_map['value'] = 'value'
  
    
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
    