from dataclasses import dataclass
from .SysmlElement import SysmlElement, SysmlType
import json
class ElementRepository:

    elements: dict[str, SysmlElement]
    def __init__(self):
        self.elements = {}

    
    def parseJson(self,jsonFile:str):
        with open(jsonFile, 'r') as f:
            data = json.load(f)
            for element_data in data:
                element = SysmlElement.parseRaw(element_data)
                self.elements[element.id] = element

    def get_all_by_type(self, type: str) -> list[SysmlElement]:
        return [e for e in self.elements.values() if e.type == type]

    def get_all_by_type(self,SysmlType: SysmlType) -> list[SysmlElement]:
        
        return [e for e in self.elements.values() if e.type == SysmlType]
    
    def get(self,id:str):
        return self.elements.get(id)