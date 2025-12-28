
from ..api.ApiModels.MetadataDefiniton import MetadataDefinition
from ..api.ApiModels.MetadataUsage import MetadataUsage
from ..api.ApiModels.Types import MetaTypes,ApiTypes
from ..api.queries import query,queryElementsByIds,queryAnyByIds,queryAnyByIdsByType,queryByType
from ..TargetModel.twin import Twin
from ..TargetModel.twin_component import Component
from ..TargetModel.twin_database import TwinDatabase,TwinDataBaseTier,TwinDataBaseType
from ..TargetModel.twin_entity import TwinEntity
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
        if model_type in globals.DATABASE.dataBases:
            wrapper: IdWrapper = globals.DATABASE.dataBases[model_type]
            return wrapper.get_by_path(path)
        return None

    def get_sub_meta_types(self) -> list[MetaTypes]:
        return []
    

    def resolve_attribute(self, element: ApiElement, attr_name: str, valueType: ApiTypes = ApiTypes.LITERALSTRING):
        # 1. Subfeatures laden (Owned + Inherited)
        all_sub_features = ApiElement.load_list_from_api(element, Fields.OWNEDFEATURE) + \
                          ApiElement.load_list_from_api(element, Fields.INHERITEDFEATURE)

        logging.info("First loop!")
        for attribute_candidate in all_sub_features:
            if attribute_candidate.get_field(Fields.NAME) == attr_name:
            
                members = ApiElement.load_list_from_api(attribute_candidate, Fields.MEMBER)
                for featureValue in members:
                    
                    if featureValue and featureValue.get_field(Fields.TYPE) == valueType.value:
                        

                        if valueType == ApiTypes.FEATUREREFERENCEEXPRESSION:
                            logging.info("FeatureReference found!,"+ str(featureValue.raw_data))
                            refElement = ApiElement.load_field_from_api(featureValue, Fields.REFERENT)
                            return refElement.get_field(Fields.NAME) if refElement else None

                        if valueType == ApiTypes.FEATURECHAINEXPRESSION:
                            logging.info("FeatureChainExpression found!,"+ str(featureValue.raw_data))
                            attribute_id = None
                            memberships = ApiElement.load_list_from_api(featureValue, Fields.MEMBERSHIP)
                            
                            for m_element in memberships:
                                if m_element.get_field(Fields.TYPE) == ApiTypes.OWNINGMEMBERSHIP.value:
                                    memberElement = ApiElement.load_field_from_api(m_element, Fields.MEMBERELEMENT)
                                    
                                    if memberElement:
                                        chainTest = memberElement.get_field(Fields.CHAININGFEATURE)
                                        chain = ApiElement.load_list_from_api(memberElement, Fields.CHAININGFEATURE)
                                        if  len(chainTest) != len(chain):
                                            raise Exception("Chain length mismatch!")
                                        if len(chain) > 0:
                                            attribute_id = chain[-1].get_field(Fields.ID)
                                            
                                            all_mapped_attribute_ids = []
                                            if MeasureAttribute in globals.DATABASE.dataBases:
                                                all_mapped_attribute_ids.extend([path[-1] for path in globals.DATABASE.dataBases[MeasureAttribute].dataTable.keys()])
                                            if ConstAttribute in globals.DATABASE.dataBases:
                                                all_mapped_attribute_ids.extend([path[-1] for path in globals.DATABASE.dataBases[ConstAttribute].dataTable.keys()])

                                            if any(attribute_id == instance_key for instance_key in all_mapped_attribute_ids):
                                                return attribute_id
                        return featureValue.get_field(Fields.VALUE)

        redef_refs = element.get_field(Fields.OWNEDREDEFINITION) or []
        for ref in redef_refs:
            redef_data_list = queryAnyByIds(element_ids=[ref['@id']], select=['redefinedFeature'], cls=ApiElement)
            if redef_data_list:
                parent_feat = ApiElement.load_field_from_api(redef_data_list[0], Fields.REDEFINEDFEATURE)
                if parent_feat:
                    result = self.resolve_attribute(parent_feat, attr_name, valueType)
                    if result is not None:
                        return result

        return None

            

class TwinRoutine(MapRoutine):
    def map(self,element: ApiElement, parent:ApiElement, my_path:list[str], current_path:list[str]) -> Twin:
        twin = Twin(name=element.get_field(Fields.NAME))
        return twin
    
    def get_sub_meta_types(self) -> list[MetaTypes]:
        return [MetaTypes.entity,MetaTypes.database,MetaTypes.condition]

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

class DatabaseRoutine(MapRoutine):
    def map(self, element: ApiElement, parent: ApiElement, my_path:list[str], current_path:list[str]) -> TwinDatabase:
        twinDatabase = TwinDatabase(name=element.get_field(Fields.NAME))
        
        parent_obj = self.get_repo_model(Twin, current_path)

        if parent_obj:
            parent_obj.add_dataBase(twinDatabase)
        else:
            logging.error("#database is ownly allowed inside a Twin!")
            raise Exception(f"Parent with path: {current_path} not found in twinMap for Database with id: {element.get_field(Fields.ID)}")
        
        dbTier = self.resolve_attribute(element, "libTwinDataBaseTier", ApiTypes.FEATUREREFERENCEEXPRESSION)
        dbType = self.resolve_attribute(element, "libTwinDataBaseType", ApiTypes.FEATUREREFERENCEEXPRESSION)
        if dbTier is not None:
            twinDatabase.tier = TwinDataBaseTier(str(dbTier).upper())
        if dbType is not None:
            twinDatabase.dbType = TwinDataBaseType(str(dbType).upper())
        return twinDatabase
    
    def get_sub_meta_types(self) -> list[MetaTypes]:
        return []
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
        
        if current_path[-1] in self.mapper.attributePortComponentMap:
            self.mapper.attributePortComponentMap[current_path[-1]].add_attribute(measureAttribute)
        else:
            logging.error(f"#measureAttribute {element.get_field(Fields.NAME)} is only allowed inside a #measure port!")
            
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
            logging.error(f"Parent Entity for Component {element.get_field(Fields.NAME)} not found at {current_path}")
            
        return twinComponent

    def get_sub_meta_types(self) -> list[MetaTypes]:
        return [MetaTypes.measure]

class PorpertyRoutine(MapRoutine):
    def map(self, element: ApiElement, parent: ApiElement, my_path: list[str], current_path: list[str]):
        comp_obj = self.get_repo_model(Component, current_path)
        
        if comp_obj:
            self.mapper.attributePortComponentMap[element.get_field(Fields.ID)] = comp_obj
        else:
            logging.error(f"#measure port {element.get_field(Fields.NAME)} must be inside a TwinComponent")
        
        return None

    def get_sub_meta_types(self) -> list[MetaTypes]:
        return [MetaTypes.measureAttribute]

class ConditionRoutine(MapRoutine):
    def map(self, element: ApiElement, parent: ApiElement, my_path: list[str], current_path: list[str]) -> Condition:
        condition = Condition(name=element.get_field(Fields.NAME))
        
        parent_twin = self.get_repo_model(Twin, current_path)
        if parent_twin:
            parent_twin.add_condition(condition)

        left_guid = self.resolve_attribute(element, "leftOperand", ApiTypes.FEATURECHAINEXPRESSION)
        right_guid = self.resolve_attribute(element, "rightOperand", ApiTypes.FEATURECHAINEXPRESSION)

        def find_operand(guid):
            if not guid: return None
            for attr_type in [MeasureAttribute, ConstAttribute]:
                if attr_type in globals.DATABASE.dataBases:
                    db = globals.DATABASE.dataBases[attr_type]
                    for path_tuple, model in db.dataTable.items():
                        if path_tuple[-1] == guid:
                            return model
            return None


        condition.leftOperand = find_operand(left_guid)
        condition.rightOperand = find_operand(right_guid)
        
        operator = self.resolve_attribute(element, "operator", ApiTypes.FEATUREREFERENCEEXPRESSION)
        if operator: 
            condition.operator = OperatorType(str(operator))

        return condition

    def get_sub_meta_types(self) -> list[MetaTypes]:
        return [MetaTypes.strategyAction]

class StrategyRoutine(MapRoutine):
    def map(self, element: ApiElement, parent: ApiElement, my_path: list[str], current_path: list[str]) -> Strategy:
        strategy = Strategy(name=element.get_field(Fields.NAME))
        
        cond_obj = self.get_repo_model(Condition, current_path)
        if cond_obj:
            cond_obj.add_strategy(strategy)
        else:
            logging.error(f"Parent Condition for Strategy {element.get_field(Fields.NAME)} not found")

        strategy.strategyType = StrategyType(str(self.resolve_attribute(element, "strategyType", ApiTypes.FEATUREREFERENCEEXPRESSION)).lower())
        strategy.pathToCode = str(self.resolve_attribute(element, "pathToCode", ApiTypes.LITERALSTRING))
        
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
            MetaTypes.database: DatabaseRoutine(self),
            MetaTypes.component: ComponentRoutine(self),
            MetaTypes.constAttribute: ConstAttributeRoutine(self),
            MetaTypes.measureAttribute: MeasureAttributeRoutine(self),
            MetaTypes.measure: PorpertyRoutine(self),
            MetaTypes.condition: ConditionRoutine(self),
            MetaTypes.strategyAction: StrategyRoutine(self),
        }

    def mapModel(self) -> list[Twin]:
        for twin_usage in self.metaDataUsageMap.get(MetaTypes.Twin, []):
            annotated_ref = twin_usage.annotatedElement[0]
            element = getElementByIdTyped(ApiElement, annotated_ref['@id'])
            
            if element:
                self.elementMapper(element, None, self.routines[MetaTypes.Twin], []) 
        
        if Twin in globals.DATABASE.dataBases:
            print("\n--- Mapped Twins JSON Output ---")
            twin_wrapper = globals.DATABASE.dataBases[Twin]
            
            for path_key, twin_obj in twin_wrapper.dataTable.items():
                if hasattr(twin_obj, 'to_dict'):
                    import json
                    print(json.dumps(twin_obj.to_dict(), indent=4))
                elif hasattr(twin_obj, 'todict'):
                    print(twin_obj.todict)
            print("----------------------------------\n")
        return list(globals.DATABASE.dataBases[Twin].dataTable.values())

    def elementMapper(self, element: ApiElement, parent: Optional[ApiElement], routine: MapRoutine, current_path: list[str]):
        my_path = current_path + [element.get_field(Fields.ID)]
        

        obj = routine.map(element, parent, my_path, current_path)
        if isinstance(obj, TwinModel):
            globals.DATABASE.add_entry(type(obj), obj, my_path)

        allowed_types = routine.get_sub_meta_types()
        all_sub_features = element.load_list_from_api(Fields.OWNEDFEATURE) + \
                          element.load_list_from_api(Fields.INHERITEDFEATURE)
        
        for sub_feature in all_sub_features:
            for m_type in allowed_types:
                if self.hasAnnotatedParentWithMetaType(sub_feature, m_type):
                    sub_routine = self.routines.get(m_type)
                    if sub_routine:
                        self.elementMapper(sub_feature, element, sub_routine, my_path)
                    break
    def hasAnnotatedParentWithMetaType(self, feature: ApiElement, metaType: MetaTypes) -> bool:
        if self.elementMetaTypeMap.get(feature.get_field(Fields.ID)) == metaType:
            return True
        redef_refs = feature.get_field(Fields.OWNEDREDEFINITION) or []
        for ref in redef_refs:
            redef_data: ApiElement = queryAnyByIds(element_ids=[ref[Fields.ID.value[0]]], select=['redefinedFeature'],cls=ApiElement)[0]
            target_ref = ApiElement.load_field_from_api(redef_data, Fields.REDEFINEDFEATURE)
            if target_ref:
                if self.hasAnnotatedParentWithMetaType(target_ref, metaType):
                    return True
                    
        return False