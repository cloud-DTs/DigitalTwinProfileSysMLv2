from sysml_v2_api_client import Project as ProjectOrigin
from .CommonElement import CommonElement

class Project(CommonElement,ProjectOrigin):
    openapi_types = {**CommonElement.openapi_types, **ProjectOrigin.openapi_types}
    attribute_map = {**CommonElement.attribute_map, **ProjectOrigin.attribute_map}