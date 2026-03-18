from dataclasses import dataclass


@dataclass
class SysMLEntity:
    id: str
    type_: str
    owner_id: str
    name: str
    qualified_name: str
