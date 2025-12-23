from .CommonElement import CommonElement

class MetadataUsage(CommonElement):
    openapi_types = CommonElement.openapi_types.copy()
    openapi_types['annotatedElement'] = 'list[str]'
    openapi_types['metadataDefinition'] = 'dict[str, str]'

    attribute_map = CommonElement.attribute_map.copy()
    attribute_map['metadataDefinition'] = 'metadataDefinition'
    attribute_map['annotatedElement'] = 'annotatedElement'

    def __init__(self):
        super().__init__()
        self._name = None
        self._metadataDefinition = None
        self._annotatedElement = None


    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def metadataDefinition(self):
        return self._metadataDefinition
    
    @metadataDefinition.setter
    def metadataDefinition(self, value):
        self._metadataDefinition = value
    
    @property
    def annotatedElement(self):
        return self._annotatedElement
    @annotatedElement.setter
    def annotatedElement(self, value):
        self._annotatedElement = value