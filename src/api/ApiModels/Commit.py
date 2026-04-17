from sysml_v2_api_client import Commit as CommitOrigin
from .CommonElement import CommonElement

class Commit(CommonElement,CommitOrigin):
    openapi_types = {**CommonElement.openapi_types, **CommitOrigin.openapi_types}
    attribute_map = {**CommonElement.attribute_map, **CommitOrigin.attribute_map}
    openapi_types["created"] = "str"
    attribute_map["created"] = "created"

    def __init__(self):
        super().__init__()
        self._created = None
    @property
    def created(self):
        return self._created
    @created.setter
    def created(self, value):
        self._created = value