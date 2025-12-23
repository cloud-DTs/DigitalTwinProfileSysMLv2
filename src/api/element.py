
import logging
import requests
from ..utils import globals
from .ApiModels.Element import Element
def getElementById(elementId:str)->dict|None:
        
        host = f"{globals.get_host()}/projects/{globals.get_project_id()}/commits/{globals.get_last_commit_id()}/elements/{elementId}"
        respone = requests.get(host)
        respone.raise_for_status()

        element_data = respone.json()
        element = Element.fromDict(element_data)
        logging.info(f"Element fetched: {element.name} with id: {element.id} and type: {element.type}")
        return element

def getElementByIdTyped(cls:type,elementId:str)->dict|None:
        
        host = f"{globals.get_host()}/projects/{globals.get_project_id()}/commits/{globals.get_last_commit_id()}/elements/{elementId}"
        respone = requests.get(host)
        respone.raise_for_status()

        element_data = respone.json()
        element = cls.fromDict(element_data)
        logging.info(f"Element fetched: {element.name} with id: {element.id} and type: {element.type}")
        return element