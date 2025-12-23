from .CommonElement import CommonElement

class MetadataDefinition(CommonElement):
    openapi_types = CommonElement.openapi_types.copy()
    openapi_types['name'] = 'str'

    attribute_map = CommonElement.attribute_map.copy()
    attribute_map['name'] = 'name'

    def __init__(self):
        super().__init__()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value