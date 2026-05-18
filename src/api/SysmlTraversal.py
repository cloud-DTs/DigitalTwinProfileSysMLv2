import logging

from .ElementRepository import ElementRepository
from .SysmlElement import SysmlElement, Field, SysmlType
from src.TargetModel.twin import Twin
from src.TargetModel.twin_measureAttribute import MeasureAttribute
from src.TargetModel.twin_constAttribute import ConstAttribute
from src.TargetModel.twin_component import Component
from typing import Optional, Set
import src.utils.globals as globals
class SysmlTraversal:
    def __init__(self, repo: ElementRepository):
        self.repo = repo
 
    def get_children(self, element: SysmlElement) -> list[SysmlElement]:
        owned = [self.repo.get(r["@id"]) for r in (element.getField(Field.OWNED_FEATURE) or [])]
        inherited = [self.repo.get(r["@id"]) for r in (element.getField(Field.INHERITED_FEATURE) or [])]
        return [e for e in owned + inherited if e]
 
    def get_non_subsetted_features(self, element: SysmlElement) -> list[SysmlElement]:
        all_features = self.get_children(element)
        subsetted_ids = set()
        for feat in all_features:
            for ref in (feat.getField(Field.OWNED_SUBSETTING) or []):
                subset_el = self.repo.get(ref["@id"])
                if subset_el:
                    target_ref = subset_el.getField(Field.SUBSETTED_FEATURE)
                    if target_ref and isinstance(target_ref, dict):
                        subsetted_ids.add(target_ref["@id"])
        return [f for f in all_features if f.id not in subsetted_ids]
 
    def find_in_hierarchy(self, element: SysmlElement, cond, visited: Optional[Set[str]] = None):
        if visited is None:
            visited = set()
        if element.id in visited:
            return False, None
        visited.add(element.id)
 
        if cond(element):
            return True, element
 
        for ref in (element.getField(Field.OWNED_REDEFINITION) or []):
            redef = self.repo.get(ref["@id"])
            if redef:
                target_ref = redef.getField(Field.SUBSETTED_FEATURE)
                if not target_ref:
                    target_ref = redef.getField(Field.REDEFINED_FEATURE)
                if target_ref and isinstance(target_ref, dict):
                    target = self.repo.get(target_ref["@id"])
                    if target:
                        found, result = self.find_in_hierarchy(target, cond, visited)
                        if found:
                            return True, result
 
        for ref in (element.getField(Field.OWNED_SUBSETTING) or []):
            subset = self.repo.get(ref["@id"])
            if subset:
                target_ref = subset.getField(Field.SUBSETTED_FEATURE)
                if target_ref and isinstance(target_ref, dict):
                    target = self.repo.get(target_ref["@id"])
                    if target:
                        found, result = self.find_in_hierarchy(target, cond, visited)
                        if found:
                            return True, result
 
        return False, None
 
    def resolve_string(self, element: SysmlElement, attr_name: str) -> Optional[str]:
        return self._resolve(element, attr_name, SysmlType.LITERAL_STRING)
 
    def resolve_int(self, element: SysmlElement, attr_name: str) -> Optional[int]:
        return self._resolve(element, attr_name, SysmlType.LITERAL_INTEGER)
 
    def resolve_bool(self, element: SysmlElement, attr_name: str) -> Optional[bool]:
        return self._resolve(element, attr_name, SysmlType.LITERAL_BOOLEAN)
 
    def resolve_enum_ref(self, element: SysmlElement, attr_name: str) -> Optional[str]:
        return self._resolve(element, attr_name, SysmlType.FEATURE_REFERENCE_EXPRESSION)
 
    def resolve_chain_ref(self, element: SysmlElement, attr_name: str):
        return self._resolve(element, attr_name, SysmlType.FEATURE_CHAIN_EXPRESSION)
 
    def _resolve(self, element: SysmlElement, attr_name: str, value_type: str):
        for candidate in self.get_children(element):
            def has_name(el: SysmlElement) -> bool:
                return el.name == attr_name
            found, _ = self.find_in_hierarchy(candidate, has_name)
            if not found:
                continue
 
            def has_value(el: SysmlElement) -> bool:
                members = el.getField(Field.MEMBER) or []
                return any(self.repo.get(m["@id"]) and self.repo.get(m["@id"]).type == value_type for m in members if isinstance(m, dict))
 
            found2, el_with_value = self.find_in_hierarchy(candidate, has_value)
            if found2 and el_with_value:
                members = el_with_value.getField(Field.MEMBER) or []
                for m_ref in members:
                    if not isinstance(m_ref, dict):
                        continue
                    fv = self.repo.get(m_ref["@id"])
                    if fv and fv.type == value_type:
                        return self._cast(fv, value_type)
        return None
 
    def _cast(self, element: SysmlElement, value_type: str):
        if value_type == SysmlType.FEATURE_REFERENCE_EXPRESSION:
            referent_ref = element.getField(Field.REFERENT)
            if referent_ref and isinstance(referent_ref, dict):
                referent = self.repo.get(referent_ref["@id"])
                return referent.name if referent else None
 
        if value_type == SysmlType.FEATURE_CHAIN_EXPRESSION:
            memberships = [self.repo.get(m["@id"]) for m in (element.getField(Field.MEMBERSHIP) or []) if isinstance(m, dict)]
            for m_el in memberships:
                if m_el and m_el.type == SysmlType.OWNING_MEMBERSHIP:
                    member_ref = m_el.getField(Field.MEMBER_ELEMENT)
                    if member_ref and isinstance(member_ref, dict):
                        member_el = self.repo.get(member_ref["@id"])
                        if member_el:
                            chain_refs = member_el.getField(Field.CHAINING_FEATURE) or []
                            path_ids = [r["@id"] for r in chain_refs if isinstance(r, dict)]
                            if path_ids:
                                for path_tuple, model in globals.DATABASE.shared_id_wrapper.dataTable.items():
                                    if not isinstance(model, (MeasureAttribute, ConstAttribute, Component)):
                                        continue
                                    if list(path_tuple[-len(path_ids):]) == path_ids:
                                        return model
            #When the field is a feature chain with only on . then we have here a fallback 
            owned_ids = {r["@id"] for r in (element.getField(Field.OWNED_FEATURE) or []) if isinstance(r, dict)}
            inherited_ids = {r["@id"] for r in (element.getField(Field.INHERITED_FEATURE) or []) if isinstance(r, dict)}
            member = element.getField(Field.MEMBER) or []
            
            resolved_ids = {r["@id"] for r in member 
                            if isinstance(r, dict) 
                            and r["@id"] not in owned_ids 
                            and r["@id"] not in inherited_ids}

            foundedMaxModel = None
            maxPathLen = -1

            for path_tuple, model in globals.DATABASE.shared_id_wrapper.dataTable.items():
                if not isinstance(model, (MeasureAttribute, ConstAttribute, Component)):
                    continue
                if path_tuple and path_tuple[-1] in resolved_ids:
                    if len(path_tuple) > maxPathLen:
                        maxPathLen = len(path_tuple)
                        foundedMaxModel = model
            
            if foundedMaxModel:
                logging.info(f"Successfully resolved to: {foundedMaxModel.name}")
            return foundedMaxModel
 
        return element.getField(Field.VALUE)
 

    def getAllParametersByParent(self,element: SysmlElement, parentName:str) -> list[SysmlElement]:
        logging.info(f"Getting all parameters for parent: {parentName}")
        res = []
        for candidate in self.get_children(element):
            def has_name(el: SysmlElement) -> bool:
                return el.name == parentName
            found, _ = self.find_in_hierarchy(candidate, has_name)
            if not found:
                continue
            logging.info(f"Found candidate {candidate.name} for parentName: {parentName}")
            res.append(candidate)
        return res