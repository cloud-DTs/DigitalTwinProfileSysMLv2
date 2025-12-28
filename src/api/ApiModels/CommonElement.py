class CommonElement:
    openapi_types = {
        'id': 'str',
        'type': 'str',
        'elementId': 'str',
    }

    attribute_map = {
        'id': '@id',
        'type': '@type',
        'elementId': 'elementId',
    }

    rawdata:dict = {}

    def __init__(self):
        self._id = None
        self._type = None
        self._elementId = None
        

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def elementId(self):
        return self._elementId
    @elementId.setter
    def elementId(self, value):
        self._elementId = value
    @classmethod
    def fromDict(cls, dict_obj):
        instance = cls()
        for attr, json_key in instance.attribute_map.items():
            if json_key in dict_obj:
                setattr(instance, attr, dict_obj[json_key])
        instance.rawdata = dict_obj
        return instance
    
    
    