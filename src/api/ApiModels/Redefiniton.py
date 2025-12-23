
from .CommonElement import CommonElement
class Redefinition(CommonElement):
    openapi_types = CommonElement.openapi_types.copy()
    openapi_types['name'] = 'str'
    openapi_types['redefinedFeature'] = 'dict[str, str]'
    openapi_types['redefiningFeature'] = 'dict[str, str]'
    attribute_map = CommonElement.attribute_map.copy()
    attribute_map['name'] = 'name'
    attribute_map['redefinedFeature'] = 'redefinedFeature'
    attribute_map['redefiningFeature'] = 'redefiningFeature'

    def __init__(self):
        super().__init__()
        self._name = None
        self._redefinedFeature = None
        self._redefiningFeature = None
        

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def redefinedFeature(self):
        return self._redefinedFeature
    @redefinedFeature.setter
    def redefinedFeature(self, value):
        self._redefinedFeature = value
    @property
    def redefiningFeature(self):
        return self._redefiningFeature
    @redefiningFeature.setter
    def redefiningFeature(self, value):
        self._redefiningFeature = value