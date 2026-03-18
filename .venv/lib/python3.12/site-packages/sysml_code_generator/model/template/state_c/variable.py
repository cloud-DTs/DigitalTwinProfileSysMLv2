from dataclasses import dataclass


@dataclass
class Variable:
    name: str
    data_type: str
    data_type_sysml: str
