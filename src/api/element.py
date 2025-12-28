from __future__ import annotations
from typing import TYPE_CHECKING
import logging
import requests
from ..utils import globals
if TYPE_CHECKING:
        from .ApiModels.Element import Element

element_cache:dict= {}
def getElementById(elementId:str)->dict|None:
        from .ApiModels.Element import Element
        host = f"{globals.get_host()}/projects/{globals.get_project_id()}/commits/{globals.get_last_commit_id()}/elements/{elementId}"
        respone = requests.get(host)
        respone.raise_for_status()

        element_data = respone.json()
        element = Element.fromDict(element_data)
        logging.info(f"Element fetched: {element.name} with id: {element.id} and type: {element.type}")
        return element

def getElementByIdTyped(cls:type,elementId:str)->dict|None:
        if elementId in element_cache:
            cached_element = element_cache[elementId]
            if isinstance(cached_element, cls):
                return cached_element
        host = f"{globals.get_host()}/projects/{globals.get_project_id()}/commits/{globals.get_last_commit_id()}/elements/{elementId}"
        respone = requests.get(host)
        respone.raise_for_status()

        element_data = respone.json()
        element = cls.fromDict(element_data)
        logging.info(f"Element fetched: {element.name} with id: {element.id} and type: {element.type}")
        return element

