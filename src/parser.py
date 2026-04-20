from src.api.ElementRepository import ElementRepository
from src.api.SysmlElement import Field, SysmlElement,SysmlType
import src.utils.globals as globals
import logging
import requests
from src.api.MetaTypes import MetaTypes
from src.mapper.ModelMapper import ModelMapper
from src.TargetModel.twin import Twin
class Parser():

    def __init__(self,elementRepository:ElementRepository):
        self.elementRepository = elementRepository
    

    metaDataDefinitonsMap:dict[str,SysmlElement] = {}
    metaDataUsageMap:dict[MetaTypes,list[SysmlElement]] = {}
    elementMetaTypeMap:dict[str,MetaTypes] = {}
    modelMapper:ModelMapper = None


    def get_all_metadata_definitions(self):
        for element in self.elementRepository.get_all_by_type(SysmlType.METADATA_DEFINITION):
            if element.name in MetaTypes.all_meta_types():
                self.metaDataDefinitonsMap[element.id] = element
                logging.info(f"MetadataDefinition parsed: {element.name} with id: {element.id}")

    def get_all_metadata_usages(self):
        for element in self.elementRepository.get_all_by_type(SysmlType.METADATA_USAGE):
            meta_def_id = element.getField(Field.METADATA_DEFINITION)
            if not meta_def_id:
                continue
            meta_def_id = meta_def_id.get("@id") if isinstance(meta_def_id, dict) else meta_def_id
            if meta_def_id in self.metaDataDefinitonsMap:
                metaTypeName = MetaTypes(self.metaDataDefinitonsMap[meta_def_id].name)
                if metaTypeName not in self.metaDataUsageMap:
                    self.metaDataUsageMap[metaTypeName] = []
                self.metaDataUsageMap[metaTypeName].append(element)
                annotated = element.getField(Field.ANNOTATED_ELEMENT)
                if annotated:
                    self.elementMetaTypeMap[annotated[0]["@id"]] = metaTypeName
                logging.info(f"MetadataUsage parsed: {metaTypeName} with id: {element.id}")    
    def parse(self)->list[Twin]:
        logging.info("Parsing all MetadataDefinitions...")
        self.get_all_metadata_definitions()
        logging.info(f"Total MetadataDefinitions parsed: {len(self.metaDataDefinitonsMap)}")
        self.get_all_metadata_usages()
        logging.info(f"Total MetadataUsages parsed: {sum(len(usages) for usages in self.metaDataUsageMap.values())}")

        self.modelMapper = ModelMapper(self.elementRepository,self.metaDataDefinitonsMap,self.metaDataUsageMap,self.elementMetaTypeMap) 
        return self.modelMapper.mapModel()