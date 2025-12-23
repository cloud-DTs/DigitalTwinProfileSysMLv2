from .CommonElement import CommonElement

class Definition(CommonElement):
    openapi_types = CommonElement.openapi_types.copy()


    attribute_map = CommonElement.attribute_map.copy()
   


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

