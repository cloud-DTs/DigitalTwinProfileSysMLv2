from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Type
import logging
import requests
from ..utils import globals

if TYPE_CHECKING:
    from .ApiModels.Element import Element

element_cache: dict[str, dict] = {}

T = TypeVar("T")

def get_raw_element(element_id: str) -> dict:
    if element_id in element_cache:
        return element_cache[element_id]

    host = f"{globals.get_host()}/projects/{globals.get_project_id()}/commits/{globals.get_last_commit_id()}/elements/{element_id}"
    response = requests.get(host)
    response.raise_for_status()

    element_data = response.json()
    element_cache[element_id] = element_data
    return element_data

def getElementById(elementId: str) -> Element | None:
    from .ApiModels.Element import Element
    try:
        element_data = get_raw_element(elementId)
        element = Element.fromDict(element_data)
        #logging.info(f"Element fetched (API/Cache): {element.name} ({element.id})")
        return element
    except Exception as e:
        logging.error(f"Error fetching element {elementId}: {e}")
        return None

def getElementByIdTyped(cls: Type[T], elementId: str) -> T | None:
    try:
        element_data = get_raw_element(elementId)
        element = cls.fromDict(element_data)
        #logging.info(f"Element fetched (API/Cache): {element.name} ({element.id})")
        return element
    except Exception as e:
        logging.error(f"Error fetching typed element {elementId}: {e}")
        return None