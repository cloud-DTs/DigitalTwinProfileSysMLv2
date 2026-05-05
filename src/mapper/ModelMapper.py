
from pathlib import Path
from ..TargetModel.twin import Twin
from ..TargetModel.twin_component import Component
from ..TargetModel.twin_database import TwinDatabase,TwinDataBaseTier,TwinDataBaseType
from ..TargetModel.twin_entity import TwinEntity
from ..TargetModel.twin_strategy import ActionOutputParameterType, FeedbackTopicType,ActionInputParameter
from ..TargetModel.twin_model import TwinModel
from ..TargetModel.twin_constAttribute import ConstAttribute
from ..TargetModel.twin_measureAttribute import MeasureAttribute, AttributeDataType
from ..TargetModel.twin_condition import Condition,CONDITION_OPERATOR as OperatorType
from ..TargetModel.twin_strategy import Strategy,StrategyType
from typing import TypeVar, Optional
from src.api.SysmlTraversal import SysmlTraversal, Field, SysmlElement
from src.api.ElementRepository import ElementRepository
import logging
from src.api.MetaTypes import MetaTypes
import json
import sys
import src.utils.globals as globals
class MapRoutine:
    T = TypeVar("T", bound=TwinModel)
 
    def __init__(self, mapper: 'ModelMapper'):
        self.mapper = mapper
 
    @property
    def traversal(self) -> SysmlTraversal:
        return self.mapper.traversal
 
    def map(self, element: SysmlElement, parent: Optional[SysmlElement], my_path: list, current_path: list) -> TwinModel:
        pass
 
    def get_repo_model(self, model_type: type, path: list):
        return globals.DATABASE.shared_id_wrapper.get_by_path(path)
 
    def get_sub_meta_types(self) -> list:
        return []
 
 
class TwinRoutine(MapRoutine):
    def map(self, element: SysmlElement, parent, my_path, current_path) -> Twin:
        twin = Twin(name=element.name)
        hotDatabaseType = self.traversal.resolve_enum_ref(element, "hotDatabaseType")
        coldDatabaseType = self.traversal.resolve_enum_ref(element, "coldDataBaseType")
        hotRetentionDays = self.traversal.resolve_int(element, "hotDatabaseRetentionDays")
        coldRetentionDays = self.traversal.resolve_int(element, "coldDatabaseRetentionDays")
 
        if hotDatabaseType is None:
            logging.warning(f"Twin {element.name} does not have a hotDatabaseType defined.")
        if hotRetentionDays is None:
            logging.warning(f"Twin {element.name} does not have a hotRetentionDays defined.")
        if coldDatabaseType is None:
            logging.warning(f"Twin {element.name} does not have a coldDatabaseType defined.")
        if coldRetentionDays is None:
            logging.warning(f"Twin {element.name} does not have a coldRetentionDays defined.")
 
        twin.hotdatabase = TwinDatabase(name=f"{element.name}_hotDatabase", id=element.id + "_hotDatabase")
        twin.hotdatabase.dbType = TwinDataBaseType(str(hotDatabaseType).upper()) if hotDatabaseType else TwinDataBaseType.RELATIONAL
        twin.hotdatabase.retentionDays = int(hotRetentionDays) if hotRetentionDays else 30
        twin.colddatabase = TwinDatabase(name=f"{element.name}_coldDatabase", id=element.id + "_coldDatabase")
        twin.colddatabase.dbType = TwinDataBaseType(str(coldDatabaseType).upper()) if coldDatabaseType else TwinDataBaseType.RELATIONAL
        twin.colddatabase.retentionDays = int(coldRetentionDays) if coldRetentionDays else 30
        return twin
 
    def get_sub_meta_types(self):
        return [MetaTypes.entity, MetaTypes.condition]
 
 
class EntityRoutine(MapRoutine):
    def map(self, element: SysmlElement, parent, my_path, parent_path) -> TwinEntity:
        twinEntity = TwinEntity(name=element.name)
        parent_obj = self.get_repo_model(Twin, parent_path) or self.get_repo_model(TwinEntity, parent_path)
        if parent_obj:
            if isinstance(parent_obj, Twin):
                parent_obj.add_entity(twinEntity)
            elif isinstance(parent_obj, TwinEntity):
                parent_obj.add_subEntity(twinEntity)
        else:
            logging.warning(f"No parent found for Entity {element.name} at path {parent_path}.")
        return twinEntity
 
    def get_sub_meta_types(self):
        return [MetaTypes.entity, MetaTypes.component, MetaTypes.constAttribute]
 
 
class ConstAttributeRoutine(MapRoutine):
    def map(self, element: SysmlElement, parent, my_path, current_path) -> ConstAttribute:
        constAttribute = ConstAttribute(name=element.name, value="")
        entity_obj = self.get_repo_model(TwinEntity, current_path)
        if entity_obj is None:
            logging.error("#constAttribute is only allowed inside a #Entity or #entity!")
            raise Exception(f"Parent not found for ConstAttribute {element.id}")
        entity_obj.add_constAttribute(constAttribute)
        value = self.traversal.resolve_string(element, "value")
        datatype = self.traversal.resolve_enum_ref(element, "dataType")
        if value is not None:
            constAttribute.value = value
        if datatype is not None:
            constAttribute.dataType = AttributeDataType(str(datatype).upper())
        return constAttribute
 
    def get_sub_meta_types(self):
        return []
 
 
class MeasureAttributeRoutine(MapRoutine):
    def map(self, element: SysmlElement, parent, my_path, current_path) -> MeasureAttribute:
        measureAttribute = MeasureAttribute(name=element.name)
        component_obj = self.get_repo_model(Component, current_path)
        if component_obj is None:
            logging.error(f"#measureAttribute {element.name} is only allowed inside a #component or #Component!")
            sys.exit(1)
        component_obj.add_attribute(measureAttribute)
        datatype = self.traversal.resolve_enum_ref(element, "dataType")
        if datatype:
            measureAttribute.dataType = AttributeDataType(str(datatype).upper())
        return measureAttribute
 
    def get_sub_meta_types(self):
        return []
 
 
class ComponentRoutine(MapRoutine):
    def map(self, element: SysmlElement, parent, my_path, current_path) -> Component:
        twinComponent = Component(name=element.name)
        entity_obj = self.get_repo_model(TwinEntity, current_path)
        if entity_obj:
            entity_obj.add_component(twinComponent)
        else:
            logging.error(f"Parent Entity for Component {element.name} not found at {current_path}.")
            sys.exit(1)
        return twinComponent
 
    def get_sub_meta_types(self):
        return [MetaTypes.measureAttribute]
 
 
class ConditionRoutine(MapRoutine):
    def map(self, element: SysmlElement, parent, my_path, current_path) -> Condition:
        condition = Condition(name=element.name)
        parent_twin = self.get_repo_model(Twin, current_path)
        if parent_twin:
            parent_twin.add_condition(condition)
        else:
            logging.error(f"Parent Twin for Condition {element.name} not found at {current_path}.")
            sys.exit(1)
        condition.leftOperand = self.traversal.resolve_chain_ref(element, "leftOperand")
        condition.rightOperand = self.traversal.resolve_chain_ref(element, "rightOperand")
        operator = self.traversal.resolve_enum_ref(element, "operator")
        if operator:
            condition.operator = OperatorType(str(operator))
        return condition
 
    def get_sub_meta_types(self):
        return [MetaTypes.strategyAction]
 
 
class StrategyRoutine(MapRoutine):
    def map(self, element: SysmlElement, parent, my_path, current_path) -> Strategy:
        strategy = Strategy(name=element.name)
        cond_obj = self.get_repo_model(Condition, current_path)
        if cond_obj:
            cond_obj.add_strategy(strategy)
        else:
            logging.error(f"Parent Condition for Strategy {element.name} not found.")
            sys.exit(1)
 
        strategy.strategyType = StrategyType(str(self.traversal.resolve_enum_ref(element, "strategyType")).lower())
        strategy.pathToCode = str(self.traversal.resolve_string(element, "pathToCode"))
        strategy.external = self.traversal.resolve_bool(element, "external")
        if strategy.external is False:
            path_obj = Path(strategy.pathToCode)
            if not path_obj.exists() or path_obj.is_file():
                logging.warning(f"Strategy {element.name} has invalid pathToCode: {strategy.pathToCode}")
            else:
                strategy.pathToCode = str(path_obj)
        strategy.feedbackTopicType = FeedbackTopicType(str(self.traversal.resolve_enum_ref(element, "feedbackTopicType")).upper())
        external_payload = self.traversal.resolve_string(element, "customPayload")
        if external_payload:
            try:
                strategy.customPaylod = json.loads(external_payload)
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding customPayload in Strategy {element.name}: {e}")
                sys.exit(1)
        strategy.componentTopic = self.traversal.resolve_chain_ref(element, "componentTopic")
        strategy.externalTopic = str(self.traversal.resolve_string(element, "externalTopic") or "")

        inputParameterNames = self.traversal.getAllParametersByParent(element, "inputParameters")
        outputParameterNames = self.traversal.getAllParametersByParent(element, "outputParameters")
        for param in inputParameterNames:
            attribute = self.traversal.resolve_chain_ref(element, param.name)
            if attribute is None:
                continue
            custom_name = param.name if param.name != "inputParameters" else attribute.name
            strategy.inputParameters.append(ActionInputParameter(customName=custom_name, attribute=attribute))
        for param_name in outputParameterNames:
            output_type = self.traversal.resolve_enum_ref(element, param_name.name)
            if output_type is None:
                continue
            if param_name.name == "outputParameters":
                logging.warning(f"Strategy {element.name} has an output parameter with no name. Skipping.")
                continue
            strategy.outputParameters.append(ActionOutputParameterType(name=param_name.name, type=output_type))


        return strategy
 
    def get_sub_meta_types(self):
        return []
 
 
class ModelMapper:
    def __init__(self, repo: ElementRepository, metaDataDefinitonsMap, metaDataUsageMap, elementMetaTypeMap):
        self.repo = repo
        self.traversal = SysmlTraversal(repo)
        self.metaDataDefinitonsMap = metaDataDefinitonsMap
        self.metaDataUsageMap = metaDataUsageMap
        self.elementMetaTypeMap = elementMetaTypeMap
        self.routines = {
            MetaTypes.Twin: TwinRoutine(self),
            MetaTypes.entity: EntityRoutine(self),
            MetaTypes.component: ComponentRoutine(self),
            MetaTypes.constAttribute: ConstAttributeRoutine(self),
            MetaTypes.measureAttribute: MeasureAttributeRoutine(self),
            MetaTypes.condition: ConditionRoutine(self),
            MetaTypes.strategyAction: StrategyRoutine(self),
        }
 
    def mapModel(self) -> list[Twin]:
        for twin_usage in self.metaDataUsageMap.get(MetaTypes.Twin, []):
            annotated = twin_usage.getField(Field.ANNOTATED_ELEMENT)
            if not annotated:
                continue
            element = self.repo.get(annotated[0]["@id"])
            if element:
                self.elementMapper(element, None, self.routines[MetaTypes.Twin], [])
        return list(filter(lambda x: isinstance(x, Twin), globals.DATABASE.shared_id_wrapper.dataTable.values()))
 
    def elementMapper(self, element: SysmlElement, parent: Optional[SysmlElement], routine: MapRoutine, current_path: list):
        my_path = current_path + [element.id]
        obj = routine.map(element, parent, my_path, current_path)
        if isinstance(obj, TwinModel):
            globals.DATABASE.add_entry(type(obj), obj, my_path)
 
        for sub_feature in self.traversal.get_non_subsetted_features(element):
            for m_type in routine.get_sub_meta_types():
                if self._has_meta_type(sub_feature, m_type):
                    sub_routine = self.routines.get(m_type)
                    if sub_routine:
                        self.elementMapper(sub_feature, element, sub_routine, my_path)
                    break
 
    def _has_meta_type(self, feature: SysmlElement, metaType: MetaTypes, visited=None) -> bool:
        def check(el: SysmlElement) -> bool:
            if self.elementMetaTypeMap.get(el.id) == metaType:
                mult = el.getField(Field.MULTIPLICITY)
                if mult is not None and str(mult).strip() != "":
                    logging.error(f"Multiplicity detected at {el.name}")
                    raise Exception("Multiplicity detected at user defined keyword.")
                return True
        return self.traversal.find_in_hierarchy(feature, check, visited)[0]
    
    