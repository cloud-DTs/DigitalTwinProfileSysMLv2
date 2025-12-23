import sysml_v2_api_client
from sysml_v2_api_client import Element
import src.utils.globals as globals
import logging
import requests
from src.api.ApiModels.MetadataDefiniton import MetadataDefinition
from src.api.ApiModels.MetadataUsage import MetadataUsage
from src.api.ApiModels.Types import MetaTypes
from src.api.queries import query

from src.mapper.ModelMapper import ModelMapper
from src.TargetModel.twin import Twin
class Parser():
    metaDataDefinitonsMap:dict[str,MetadataDefinition] = {}
    metaDataUsageMap:dict[MetaTypes,list[MetadataUsage]] = {}
    elementMetaTypeMap:dict[str,MetaTypes] = {}
    modelMapper:ModelMapper = None
    def get_all_metadata_definitions(self):
        query_input = {
        '@type':'Query',
        'select': ['name','@id','@type','owner'],
        'where': {
          '@type': 'CompositeConstraint',
          'operator': 'and',
          'constraint': [
              {
                  '@type': 'PrimitiveConstraint',
                  'inverse': False,
                  'operator': '=',
                  'property': '@type',
                  'value': ['MetadataDefinition']
              }
          ]
        }
        }
        response:list[MetadataDefinition] = query(MetadataDefinition,query_input)
        for metaDataDefiniton in response:
            if metaDataDefiniton.name in MetaTypes.all_meta_types():
                self.metaDataDefinitonsMap[metaDataDefiniton.id] = metaDataDefiniton
                logging.info(f"MetadataDefinition parsed: {metaDataDefiniton.name} with id: {metaDataDefiniton.id}")

    def get_all_metadata_usages(self):
        query_input = {
        '@type':'Query',
        'select': ['name','@id','@type','owner','metadataDefinition','annotatedElement'],
        'where': {
          '@type': 'CompositeConstraint',
          'operator': 'and',
          'constraint': [
              {
                  '@type': 'PrimitiveConstraint',
                  'inverse': False,
                  'operator': '=',
                  'property': '@type',
                  'value': ['MetadataUsage']
              }
          ]
        }
        }
        response:list[MetadataUsage] = query(MetadataUsage,query_input)
        for metaDataUsage in response:
            if metaDataUsage.metadataDefinition['@id'] in self.metaDataDefinitonsMap:
                metaTypeName = self.metaDataDefinitonsMap[metaDataUsage.metadataDefinition['@id']].name
                metaTypeName = MetaTypes(metaTypeName)
                if metaTypeName not in self.metaDataUsageMap:
                    self.metaDataUsageMap[metaTypeName] = []
                self.metaDataUsageMap[metaTypeName].append(metaDataUsage)
                self.elementMetaTypeMap[metaDataUsage.annotatedElement[0]['@id']] = metaTypeName
                logging.info(f"MetadataUsage parsed: {metaTypeName} with id: {metaDataUsage.id}")
    
    def parse(self)->list[Twin]:
        logging.info("Parsing all MetadataDefinitions...")
        self.get_all_metadata_definitions()
        logging.info(f"Total MetadataDefinitions parsed: {len(self.metaDataDefinitonsMap)}")
        self.get_all_metadata_usages()
        logging.info(f"Total MetadataUsages parsed: {sum(len(usages) for usages in self.metaDataUsageMap.values())}")

        self.modelMapper = ModelMapper(self.metaDataDefinitonsMap,self.metaDataUsageMap,self.elementMetaTypeMap) 
        self.modelMapper.mapModel()
        return []