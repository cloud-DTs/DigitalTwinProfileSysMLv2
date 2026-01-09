
from ..api.ApiModels.MetadataDefiniton import MetadataDefinition
from ..api.ApiModels.MetadataUsage import MetadataUsage
from ..api.ApiModels.Types import MetaTypes,ApiTypes
from ..api.queries import query,queryElementsByIds,queryAnyByIds,queryAnyByIdsByType,queryByType
from ..TargetModel.twin import Twin
from ..TargetModel.twin_component import Component
from ..TargetModel.twin_database import TwinDatabase,TwinDataBaseTier,TwinDataBaseType
from ..TargetModel.twin_entity import TwinEntity
from ..TargetModel.twin_strategy import FeedbackTopicType
from ..TargetModel.twin_model import TwinModel
from ..TargetModel.twin_constAttribute import ConstAttribute
from ..TargetModel.twin_measureAttribute import MeasureAttribute, AttributeDataType
from ..TargetModel.twin_condition import Condition,CONDITION_OPERATOR as OperatorType
from ..TargetModel.twin_strategy import Strategy,StrategyType
from ..api.ApiModels.Element import Element
from ..api.ApiModels.Redefiniton import Redefinition
from ..api.ApiModels.FeatureValue import FeatureValue
from typing import Optional, TypeVar, Type
from ..api.element import getElementByIdTyped, getElementById
import logging
import sys
import json
from ..utils import globals
from ..utils.IdDatabase import IdWrapper
from ..api.ApiModels.ApiElement import ApiElement, Fields

class MapRoutine():
    T = TypeVar("T", bound=TwinModel)

    def __init__(self, mapper: 'ModelMapper'):
        self.mapper = mapper
    
    def map(self, element: ApiElement, parent: ApiElement, my_path: list[str], current_path: list[str]) -> T:
        pass

    def get_repo_model(self, model_type: type, path: list[str]) -> Optional[T]:
        return globals.DATABASE.shared_id_wrapper.get_by_path(path)

    def get_sub_meta_types(self) -> list[MetaTypes]:
        return []
    

    def castFeatureValue(self, featureValue: ApiElement, valueType: ApiTypes) -> FeatureValue:
        if valueType == ApiTypes.FEATUREREFERENCEEXPRESSION:
            refElement = ApiElement.load_field_from_api(featureValue, Fields.REFERENT)
            return refElement.get_field(Fields.NAME) if refElement else None

        if valueType == ApiTypes.FEATURECHAINEXPRESSION:
            memberships = ApiElement.load_list_from_api(featureValue, Fields.MEMBERSHIP)

            for m_element in memberships:
                if m_element.get_field(Fields.TYPE) == ApiTypes.OWNINGMEMBERSHIP.value:
                    memberElement = ApiElement.load_field_from_api(m_element, Fields.MEMBERELEMENT)

                    if memberElement:
                        chainTest = memberElement.get_field(Fields.CHAININGFEATURE)
                        chain = ApiElement.load_list_from_api(memberElement, Fields.CHAININGFEATURE)
                        path_ids = [ch.get_field(Fields.ID) for ch in chain]
                        if  len(chainTest) != len(chain):
                            raise Exception("Chain length mismatch!")
                        if len(chain) > 0:
                            for path_tuple, model in globals.DATABASE.shared_id_wrapper.dataTable.items():
                                if not isinstance(model, MeasureAttribute) and not isinstance(model, ConstAttribute) and not isinstance(model, Component):
                                    continue
                                if list(path_tuple[-len(path_ids):]) == path_ids:
                                    return model


        return featureValue.get_field(Fields.VALUE)

    def resolve_attribute(self, element: ApiElement, attr_name: str, valueType: ApiTypes = ApiTypes.LITERALSTRING):
        all_sub_features = element.load_list_from_api(Fields.OWNEDFEATURE) + \
                           element.load_list_from_api(Fields.INHERITEDFEATURE)

        for attribute_candidate in all_sub_features:
            if self.elmentIsAttr(attribute_candidate, attr_name):
                def has_value_data(el: ApiElement) -> bool:
                    members = el.load_list_from_api(Fields.MEMBER)
                    return any(m.get_field(Fields.TYPE) == valueType.value for m in members)

                found, element_with_value = attribute_candidate.find_in_hierarchy(has_value_data)

                if found and element_with_value:
                    members = element_with_value.load_list_from_api(Fields.MEMBER)
                    for featureValue in members:
                        if featureValue and featureValue.get_field(Fields.TYPE) == valueType.value:
                            return self.castFeatureValue(featureValue, valueType)
        return None
    
    def elmentIsAttr(self, element: ApiElement, attr_name: str) -> bool:
        def checkName(element: ApiElement) -> bool:
            return element.get_field(Fields.NAME) == attr_name
        return element.find_in_hierarchy(checkName)[0]

            

class TwinRoutine(MapRoutine):
    def map(self,element: ApiElement, parent:ApiElement, my_path:list[str], current_path:list[str]) -> Twin:
        twin = Twin(name=element.get_field(Fields.NAME))

        hotDatabaseType = self.resolve_attribute(element, "hotDatabaseType", ApiTypes.FEATUREREFERENCEEXPRESSION)
        coldDatabaseType = self.resolve_attribute(element, "coldDataBaseType", ApiTypes.FEATUREREFERENCEEXPRESSION)
        hotRetentionDays = self.resolve_attribute(element, "hotDatabaseRetentionDays", ApiTypes.LITERALINTEGER)
        coldRetentionDays = self.resolve_attribute(element, "coldDatabaseRetentionDays", ApiTypes.LITERALINTEGER)
        if hotDatabaseType is None:
            logging.warning(f"Twin {element.get_field(Fields.NAME)} does not have a hotDatabaseType defined.")
        if hotRetentionDays is None:
            logging.warning(f"Twin {element.get_field(Fields.NAME)} does not have a hotRetentionDays defined.")
        

        if coldDatabaseType is None:
            logging.warning(f"Twin {element.get_field(Fields.NAME)} does not have a coldDatabaseType defined.")
        if coldRetentionDays is None:
            logging.warning(f"Twin {element.get_field(Fields.NAME)} does not have a coldRetentionDays defined.")
        
        twin.hotdatabase = TwinDatabase(name=f"{element.get_field(Fields.NAME)}_hotDatabase",id=element.get_field(Fields.ID)+"_hotDatabase")
        twin.hotdatabase.dbType = TwinDataBaseType(str(hotDatabaseType).upper()) if hotDatabaseType else TwinDataBaseType.RELATIONAL
        twin.hotdatabase.retentionDays = int(hotRetentionDays) if hotRetentionDays else 30
        twin.colddatabase = TwinDatabase(name=f"{element.get_field(Fields.NAME)}_coldDatabase",id=element.get_field(Fields.ID)+"_coldDatabase")
        twin.colddatabase.dbType = TwinDataBaseType(str(coldDatabaseType).upper()) if coldDatabaseType else TwinDataBaseType.RELATIONAL
        twin.colddatabase.retentionDays = int(coldRetentionDays) if coldRetentionDays else 30
        
        return twin
    
    def get_sub_meta_types(self) -> list[MetaTypes]:
        return [MetaTypes.entity,MetaTypes.condition]

class EntityRoutine(MapRoutine):
    def map(self, element: ApiElement, parent: ApiElement, my_path: list[str], parent_path: list[str]) -> TwinEntity:
        twinEntity = TwinEntity(name=element.get_field(Fields.NAME))
        
        parent_obj = self.get_repo_model(Twin, parent_path) or self.get_repo_model(TwinEntity, parent_path)
        
        if parent_obj:
            if isinstance(parent_obj, Twin):
                parent_obj.add_entity(twinEntity)
            elif isinstance(parent_obj, TwinEntity):
                parent_obj.add_subEntity(twinEntity)
        else:
            logging.warning(f"No parent found for Entity {element.get_field(Fields.NAME)} at path {parent_path}")
            
        return twinEntity
    def get_sub_meta_types(self) -> list[MetaTypes]:
        return [MetaTypes.entity,MetaTypes.component,MetaTypes.constAttribute]


class ConstAttributeRoutine(MapRoutine):
    def map(self, element: ApiElement, parent: ApiElement, my_path:list[str], current_path:list[str]) -> ConstAttribute:
        constAttribute = ConstAttribute(name=element.get_field(Fields.NAME), value="")
        
        entity_obj = self.get_repo_model(TwinEntity, current_path)

        if entity_obj is None:
            logging.error("#constAttribute is ownly allowed inside a Component!")
            raise Exception(f"Parent with path: {current_path} not found in componentMap for ConstAttribute with id: {element.get_field(Fields.ID)}")
        
        entity_obj.add_constAttribute(constAttribute)
        value = self.resolve_attribute(element,"value", ApiTypes.LITERALSTRING)
        datatype = self.resolve_attribute(element, "dataType", ApiTypes.FEATUREREFERENCEEXPRESSION)

        if value is not None:
            constAttribute.value = value
        if datatype is not None:
            constAttribute.dataType = AttributeDataType(str(datatype).upper())

        return constAttribute
    
    def get_sub_meta_types(self) -> list[MetaTypes]:
        return []
class MeasureAttributeRoutine(MapRoutine):
    def map(self, element: ApiElement, parent: Element, my_path: list[str], current_path: list[str]) -> MeasureAttribute:
        measureAttribute = MeasureAttribute(name=ApiElement.get_field(element, Fields.NAME))
        
        component_obj = self.get_repo_model(Component, current_path)
        if component_obj is None:
            logging.error(f"#measureAttribute {element.get_field(Fields.NAME)} is only allowed inside a #component or #Component!")
            sys.exit(1)
        
        component_obj.add_attribute(measureAttribute)
        datatype = self.resolve_attribute(element, "dataType", ApiTypes.FEATUREREFERENCEEXPRESSION)
        if datatype:
            measureAttribute.dataType = AttributeDataType(str(datatype).upper())
            
        return measureAttribute

    def get_sub_meta_types(self) -> list[MetaTypes]:
        return []

class ComponentRoutine(MapRoutine):
    def map(self, element: ApiElement, parent: ApiElement, my_path: list[str], current_path: list[str]) -> Component:
        twinComponent = Component(name=element.get_field(Fields.NAME))
        
        entity_obj = self.get_repo_model(TwinEntity, current_path)
        if entity_obj:
            entity_obj.add_component(twinComponent)
        else:
            logging.error(f"Parent Entity for Component {element.get_field(Fields.NAME)} not found at {current_path}. #component is only allowed inside a #entity or #Entity!")
            sys.exit(1)
            
        return twinComponent

    def get_sub_meta_types(self) -> list[MetaTypes]:
        return [MetaTypes.measureAttribute]


class ConditionRoutine(MapRoutine):
    def map(self, element: ApiElement, parent: ApiElement, my_path: list[str], current_path: list[str]) -> Condition:
        condition = Condition(name=element.get_field(Fields.NAME))
        
        parent_twin = self.get_repo_model(Twin, current_path)
        if parent_twin:
            parent_twin.add_condition(condition)
        else:
            logging.error(f"Parent Twin for Condition {element.get_field(Fields.NAME)} not found at {current_path}. #condition is only allowed inside a #twin!")
            sys.exit(1)

        condition.leftOperand = self.resolve_attribute(element, "leftOperand", ApiTypes.FEATURECHAINEXPRESSION)
        condition.rightOperand = self.resolve_attribute(element, "rightOperand", ApiTypes.FEATURECHAINEXPRESSION)
        
        operator = self.resolve_attribute(element, "operator", ApiTypes.FEATUREREFERENCEEXPRESSION)
        if operator: 
            condition.operator = OperatorType(str(operator))

        return condition

    def get_sub_meta_types(self) -> list[MetaTypes]:
        return [MetaTypes.strategyAction]

class StrategyRoutine(MapRoutine):
    def map(self, element: ApiElement, parent: ApiElement, my_path: list[str], current_path: list[str]) -> Strategy:
        strategy = Strategy(name=element.get_field(Fields.NAME))
        
        print("Finding parent Condition for Strategy at name: " + element.get_field(Fields.NAME))
        cond_obj = self.get_repo_model(Condition, current_path)
        if cond_obj:
            cond_obj.add_strategy(strategy)
        else:
            logging.error(f"Parent Condition for Strategy {element.get_field(Fields.NAME)} not found. #strategyAction is only allowed inside a #condition!")
            sys.exit(1)

        strategy.strategyType = StrategyType(str(self.resolve_attribute(element, "strategyType", ApiTypes.FEATUREREFERENCEEXPRESSION)).lower())
        strategy.pathToCode = str(self.resolve_attribute(element, "pathToCode", ApiTypes.LITERALSTRING))
        strategy.external = self.resolve_attribute(element, "external", ApiTypes.LITERALBOOLEAN)
        strategy.feedbackTopicType = FeedbackTopicType(str(self.resolve_attribute(element, "feedbackTopicType", ApiTypes.FEATUREREFERENCEEXPRESSION)).upper())
        external_payload = self.resolve_attribute(element, "customPayload", ApiTypes.LITERALSTRING)
        if external_payload:
            try:
                strategy.customPaylod = json.loads(external_payload)
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON for customPayload in Strategy {element.get_field(Fields.NAME)}: {e}. CustomPayload needs to be a valid JSON string.")
                strategy.customPaylod = None
                sys.exit(1)
        
        strategy.componentTopic = self.resolve_attribute(element, "componentTopic", ApiTypes.FEATURECHAINEXPRESSION)
       
        strategy.externalTopic = str(self.resolve_attribute(element, "externalTopic", ApiTypes.LITERALSTRING)) or ""
        return strategy

    def get_sub_meta_types(self) -> list[MetaTypes]:
        return []
class ModelMapper():
    def __init__(self, metaDataDefinitonsMap, metaDataUsageMap, elementMetaTypeMap):
        self.metaDataDefinitonsMap = metaDataDefinitonsMap
        self.metaDataUsageMap = metaDataUsageMap
        self.elementMetaTypeMap = elementMetaTypeMap
        self.attributePortComponentMap = {}
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
            annotated_ref = twin_usage.annotatedElement[0]
            element = getElementByIdTyped(ApiElement, annotated_ref['@id'])
            
            if element:
                self.elementMapper(element, None, self.routines[MetaTypes.Twin], []) 
        
        return list(filter(lambda x: isinstance(x, Twin), globals.DATABASE.shared_id_wrapper.dataTable.values()))

    def elementMapper(self, element: ApiElement, parent: Optional[ApiElement], routine: MapRoutine, current_path: list[str]):
        
        
        my_path = current_path + [element.get_field(Fields.ID)]
        

        obj = routine.map(element, parent, my_path, current_path)
        if isinstance(obj, TwinModel):
            globals.DATABASE.add_entry(type(obj), obj, my_path)

        allowed_types = routine.get_sub_meta_types()
        all_sub_features = element.load_list_from_api(Fields.OWNEDFEATURE) + \
                          element.load_list_from_api(Fields.INHERITEDFEATURE)
        subsetted_ids = []
        for feat in all_sub_features:
            subset_refs = feat.get_field(Fields.OWNEDSUBSETTING) or []
            for ref in subset_refs:
                subset_element = getElementByIdTyped(ApiElement, ref['@id'])
                if subset_element:
                    target = subset_element.load_field_from_api(Fields.SUBSETTEDFEATURE)
                    if target:
                        subsetted_ids.append(target.id)
        for sub_feature in all_sub_features:
            if sub_feature.id in subsetted_ids:
                continue
            for m_type in allowed_types:
                if self.hasAnnotatedParentWithMetaType(sub_feature, m_type):
                    sub_routine = self.routines.get(m_type)
                    if sub_routine:
                        self.elementMapper(sub_feature, element, sub_routine, my_path)
                    break
    def hasAnnotatedParentWithMetaType(self, feature: ApiElement, metaType: MetaTypes, visited=None) -> bool:

        def checkMetaType(element:ApiElement) -> bool:
            if self.elementMetaTypeMap.get(element.id) == metaType:
                mult = ApiElement.get_field(element, Fields.MULTIPLICITY)
                if mult is not None and str(mult).strip() != "":
                    logging.error("Parsing stopped. We do not allow multiplicities at our user defined keywords")
                    logging.error(f"{ApiElement.get_field(element, Fields.NAME)} has multiplicity: {mult}")
                    raise Exception("Multiplicity detected at user defined keyword.")
                return True
            
        return feature.find_in_hierarchy(checkMetaType, visited)[0]