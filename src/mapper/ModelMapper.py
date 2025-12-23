
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
from typing import TypeVar, Type
from ..api.element import getElementById,getElementByIdTyped
import logging
import sys
import json


class MapRoutine():

    T = TypeVar("T", bound=TwinModel)

    def __init__(self,mapper:'ModelMapper'):
        self.mapper = mapper
    
    def map(self, element: Element, parent: Element, instance_id: str, parent_instance_id: str)->T:
        pass

    def get_sub_meta_types(self) -> list[MetaTypes]:
        pass

    def resolve_attribute(self, element: Element, attr_name: str, valueType: ApiTypes = ApiTypes.LITERALSTRING):
        all_sub_features = (element.ownedFeature or []) + (element.inheritedFeature or [])

        for sub_ref in all_sub_features:
            attribute_candidate: Element = getElementById(sub_ref['@id'])
            
            if attribute_candidate.name == attr_name:
                for att in (attribute_candidate.member or []):
                    featureValue:FeatureValue = getElementByIdTyped(FeatureValue, att['@id']) 
                    if(featureValue and featureValue.type == valueType.value):
                        if(valueType == ApiTypes.FEATUREREFERENCE):
                            refE = featureValue.rawdata['referent']
                            refElement = getElementById(refE['@id'])
                            return refElement.name

                        #featurechainnexpressio       -> OwninGMembeship                  -> Feature 
                        #		               -> memership 			->memeberElement            -> chaining feature durchiterien
                        if (valueType == ApiTypes.FeatureChainExpression):
                            attribute_id = None
                            for membership_id in featureValue.membership:
                                memebership:Element = getElementByIdTyped(Element, membership_id['@id'])
                                if(memebership.type == ApiTypes.OwningMembership.value):
                                    memberElementId = memebership.memberElement['@id']

                                    feat:Element = getElementByIdTyped(Element, memberElementId)
                                    chain = feat.chainingFeature

                                    if len(chain) > 0:
                                        attribute_id = chain[-1]['@id']
                                        all_mapped_attribute_ids = list(self.mapper.measureAttributeMap.keys()) + list(self.mapper.constAttributeMap.keys())

                                        if any(attribute_id in instance_key for instance_key in all_mapped_attribute_ids):
                                            return attribute_id
                                    
                        return featureValue.value
                        
        
        redef_refs = getattr(element, 'ownedRedefinition', []) or []
        for ref in redef_refs:
            redef_data: Redefinition = queryAnyByIds(element_ids=[ref['@id']], select=['redefinedFeature'], cls=Redefinition)[0]
            if redef_data.redefinedFeature:
                parent_feat = getElementById(redef_data.redefinedFeature['@id'])
                return self.resolve_attribute(parent_feat, attr_name, valueType)

        return None
            

class TwinRoutine(MapRoutine):
    def map(self, element: Element, parent: Element, instance_id: str, parent_instance_id: str) -> Twin:
        twin = Twin(name=element.name, id=instance_id)
        self.mapper.twinMap[instance_id] = twin
        return twin
    
    def get_sub_meta_types(self) -> list[MetaTypes]:
        return [MetaTypes.entity,MetaTypes.database,MetaTypes.condition]

class EntityRoutine(MapRoutine):
    def map(self, element: Element, parent: Element, instance_id: str, parent_instance_id: str) -> TwinEntity:
        twinEntity = TwinEntity(name=element.name, id=instance_id)
        self.mapper.entityMap[instance_id] = twinEntity
        
        if parent_instance_id in self.mapper.twinMap:
            self.mapper.twinMap[parent_instance_id].add_entity(twinEntity)
        elif parent_instance_id in self.mapper.entityMap:
            self.mapper.entityMap[parent_instance_id].add_subEntity(twinEntity)
        
        return twinEntity
    def get_sub_meta_types(self) -> list[MetaTypes]:
        return [MetaTypes.entity,MetaTypes.component,MetaTypes.constAttribute]

class DatabaseRoutine(MapRoutine):
    def map(self, element: Element, parent: Element, instance_id: str, parent_instance_id: str) -> TwinDatabase:
        twinDatabase = TwinDatabase(name=element.name, id=instance_id)
        self.mapper.databaseMap[instance_id] = twinDatabase
        
        if parent_instance_id not in self.mapper.twinMap:
            logging.error("#database is ownly allowed inside a Twin!")
            raise Exception(f"Parent with id: {parent_instance_id} not found in twinMap for Database with id: {instance_id}")
        self.mapper.twinMap[parent_instance_id].add_dataBase(twinDatabase)

        dbTier = self.resolve_attribute(element, "libTwinDataBaseTier", ApiTypes.FEATUREREFERENCE)
        dbType = self.resolve_attribute(element, "libTwinDataBaseType", ApiTypes.FEATUREREFERENCE)
        if dbTier is not None:
            twinDatabase.tier = TwinDataBaseTier(str(dbTier).upper())
        if dbType is not None:
            twinDatabase.dbType = TwinDataBaseType(str(dbType).upper())
        return twinDatabase
    
    
    def get_sub_meta_types(self) -> list[MetaTypes]:
        return []
class ConstAttributeRoutine(MapRoutine):
    def map(self, element: Element, parent: Element, instance_id: str, parent_instance_id: str) -> ConstAttribute:
        constAttribute = ConstAttribute(name=element.name, id=instance_id, value="")
        self.mapper.constAttributeMap[instance_id] = constAttribute
        
        if parent_instance_id not in self.mapper.entityMap:
            logging.error("#constAttribute is ownly allowed inside a Component!")
            raise Exception(f"Parent with id: {parent_instance_id} not found in componentMap for ConstAttribute with id: {instance_id}")
        self.mapper.entityMap[parent_instance_id].add_constAttribute(constAttribute)
        value = self.resolve_attribute(element,"value", ApiTypes.LITERALSTRING)
        datatype = self.resolve_attribute(element, "dataType", ApiTypes.FEATUREREFERENCE)

        if value is not None:
            constAttribute.value = value
        if datatype is not None:
            constAttribute.dataType = AttributeDataType(str(datatype).upper())

        return constAttribute
    
    def get_sub_meta_types(self) -> list[MetaTypes]:
        return []
class MeasureAttributeRoutine(MapRoutine):
    def map(self, element: Element, parent: Element, instance_id: str, parent_instance_id: str) -> MeasureAttribute:
        measureAttribute = MeasureAttribute(name=element.name, id=instance_id)
        self.mapper.measureAttributeMap[instance_id] = measureAttribute
        
       
        if parent_instance_id not in self.mapper.attributePortComponentMap:
            logging.error("#measureAttribute is ownly allowed inside a #measure port!")
            raise Exception(f"Parent {parent.name} with id: {parent_instance_id} not found in componentMap for MeasureAttribute with id: {element.id}")
        self.mapper.attributePortComponentMap[parent_instance_id].add_attribute(measureAttribute)
        datatype = self.resolve_attribute(element, "dataType", ApiTypes.FEATUREREFERENCE)
        
        if datatype is not None:
            measureAttribute.dataType = AttributeDataType(str(datatype).upper())
        return measureAttribute
    
    def get_sub_meta_types(self) -> list[MetaTypes]:
        return []
class ComponentRoutine(MapRoutine):
    def map(self, element: Element, parent: Element, instance_id: str, parent_instance_id: str) -> Component:
        twinComponent = Component(id=instance_id, name=element.name)
        
        if parent_instance_id not in self.mapper.entityMap:
            logging.error("#component is ownly allowed inside a TwinEntity!")
            raise Exception(f"Parent with id: {parent_instance_id} not found in entityMap for Component with id: {element.id}")
        self.mapper.entityMap[parent_instance_id].add_component(twinComponent)
        self.mapper.componentMap[instance_id] = twinComponent
        return twinComponent
    
    def get_sub_meta_types(self) -> list[MetaTypes]:
        return [MetaTypes.measure]
class PorpertyRoutine(MapRoutine):
    def map(self, element: Element, parent: Element, instance_id: str, parent_instance_id: str):

        if parent_instance_id not in self.mapper.componentMap:
            logging.error("#measure is ownly allowed inside a TwinComponent!")
            raise Exception(f"Parent with id: {parent_instance_id} not found in componentMap for Measure with id: {element.id}")
        self.mapper.attributePortComponentMap[instance_id] = self.mapper.componentMap[parent_instance_id]
    
    def get_sub_meta_types(self) -> list[MetaTypes]:
        return [MetaTypes.measureAttribute]
class ConditionRoutine(MapRoutine):
    def map(self, element: Element, parent: Element, instance_id: str, parent_instance_id: str) -> Condition:
        condition = Condition(name=element.name, id=instance_id)
        self.mapper.conditionMap[instance_id] = condition
        
        if parent_instance_id not in self.mapper.twinMap:
            logging.error("#condition is only allowed inside a Twin!")
            raise Exception(f"Parent with id: {parent_instance_id} not found in twinMap for Condition with id: {element.id}")
        
        self.mapper.twinMap[parent_instance_id].add_condition(condition)

        name = self.resolve_attribute(element, "name", ApiTypes.LITERALSTRING)
        operator = self.resolve_attribute(element, "operator", ApiTypes.FEATUREREFERENCE)
        left_guid = self.resolve_attribute(element, "leftOperand", ApiTypes.FeatureChainExpression)
        right_guid = self.resolve_attribute(element, "rightOperand", ApiTypes.FeatureChainExpression)

        if name: condition.name = name
        if operator: condition.operator = OperatorType(str(operator))
        
        def find_instance_attribute(guid):
            if not guid: return None
            for map_dict in [self.mapper.measureAttributeMap, self.mapper.constAttributeMap]:
                for inst_id, attr_obj in map_dict.items():
                    if guid in inst_id:
                        return attr_obj
            return None

        condition.leftOperand = find_instance_attribute(left_guid)
        condition.rightOperand = find_instance_attribute(right_guid)

        return condition
    
    def get_sub_meta_types(self) -> list[MetaTypes]:
        return [MetaTypes.strategyAction]

class StrategyRoutine(MapRoutine):
    def map(self, element: Element, parent: Element, instance_id: str, parent_instance_id: str) -> Strategy:
        strategy = Strategy(name=element.name, id=instance_id)
        self.mapper.strategyMap[instance_id] = strategy
        
        if parent_instance_id not in self.mapper.conditionMap:
            logging.error("#strategyAction is ownly allowed inside a Condition!")
            raise Exception(f"Parent with id: {parent_instance_id} not found in conditionMap for Strategy with id: {element.id}")
        self.mapper.conditionMap[parent_instance_id].add_strategy(strategy)

        name = self.resolve_attribute(element,"name", ApiTypes.LITERALSTRING)
        strategyType = self.resolve_attribute(element, "strategyType", ApiTypes.FEATUREREFERENCE)
        pathToCode = self.resolve_attribute(element, "pathToCode", ApiTypes.LITERALSTRING)
        if name is not None:
            strategy.name = name
        if strategyType is not None:
            strategy.strategyType = StrategyType(str(strategyType).lower())
        if pathToCode is not None:
            strategy.pathToCode = str(pathToCode)
        return strategy
    
    def get_sub_meta_types(self) -> list[MetaTypes]:
        return []
class ModelMapper():
    def __init__(self,metaDataDefinitonsMap:dict[str,MetadataDefinition],metaDataUsageMap:dict[MetaTypes,list[MetadataUsage]], elementMetaTypeMap:dict[str,MetaTypes]):
        self.metaDataDefinitonsMap = metaDataDefinitonsMap
        self.metaDataUsageMap = metaDataUsageMap
        self.twinMap:dict[str,Twin] = {}
        self.entityMap:dict[str,TwinEntity] = {}
        self.databaseMap:dict[str,TwinDatabase] = {}
        self.componentMap:dict[str,Component] = {}
        self.constAttributeMap:dict[str,ConstAttribute] = {}
        self.measureAttributeMap:dict[str,MeasureAttribute] = {}
        self.conditionMap:dict[str,Condition] = {}
        self.strategyMap:dict[str,Strategy] = {}
        self.attributePortComponentMap: dict[str, Component] = {}
        self.enbumartionUsageMap: dict[str, str] = {}
        self.inheritedFeaturesMap: list[str] = []
        enumer = queryByType(select=[], apiType=ApiTypes.FEATUREREFERENCE.value, cls=Element)
        for enum in enumer:
            self.enbumartionUsageMap[enum.id] = enum.name 
        self.pendingEntities: dict[str, list[TwinEntity]] = {}
        self.elementMetaTypeMap:dict[str,MetaTypes] = elementMetaTypeMap
        self.routines: dict[MetaTypes, MapRoutine] = {
            MetaTypes.Twin: TwinRoutine(self),
            MetaTypes.entity: EntityRoutine(self),
            MetaTypes.database: DatabaseRoutine(self),
            MetaTypes.component: ComponentRoutine(self),
            MetaTypes.constAttribute:ConstAttributeRoutine(self),
            MetaTypes.measureAttribute:MeasureAttributeRoutine(self),
            MetaTypes.measure:PorpertyRoutine(self),
            MetaTypes.condition:ConditionRoutine(self),
            MetaTypes.strategyAction:StrategyRoutine(self),
        
        }
    def mapModel(self)->list[Twin]:

        for twin in self.metaDataUsageMap.get(MetaTypes.Twin,[]):
            logging.info(f"Mapping Twin with id: {twin.annotatedElement[0]['@id']}")
            element: Element = getElementById(twin.annotatedElement[0]['@id'])
            self.elementMapper(element, None, self.routines[MetaTypes.Twin])           
        
        for twin in self.twinMap.values():
            print(json.dumps(twin.to_dict(), indent=2))
        return self.twinMap.values()
    
    def elementMapper(self, element: Element, parent: Element, routine: MapRoutine, parent_instance_id: str = None):
        instance_id = element.id
        if parent_instance_id:
            instance_id = f"{element.id}_{parent_instance_id}"
        obj: TwinModel = routine.map(element, parent, instance_id, parent_instance_id)

        all_sub_features = (element.ownedFeature or []) + (element.inheritedFeature or [])
        if not all_sub_features:
            return

        allowed_types = routine.get_sub_meta_types()
        
        for sub_ref in all_sub_features:
            sub_feature: Element = getElementById(sub_ref['@id'])
            
            for m_type in allowed_types:
                if self.hasAnnotatedParentWithMetaType(sub_feature, m_type):
                    sub_routine = self.routines.get(m_type)
                    if sub_routine:
                        self.elementMapper(sub_feature, element, sub_routine, instance_id)
                    break
                    


    def hasAnnotatedParentWithMetaType(self, feature: Element, metaType: MetaTypes) -> bool:
        if self.elementMetaTypeMap.get(feature.id) == metaType:
            return True
        redef_refs = getattr(feature, 'ownedRedefinition', []) or []
        for ref in redef_refs:
            redef_data: Redefinition = queryAnyByIds(element_ids=[ref['@id']], select=['redefinedFeature'],cls=Redefinition)[0]
            target_ref = redef_data.redefinedFeature
            if target_ref:
                parent_feat = getElementById(target_ref['@id'])
                if self.hasAnnotatedParentWithMetaType(parent_feat, metaType):
                    return True
                    
        return False