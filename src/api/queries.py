from .ApiModels.CommonElement import CommonElement
import logging
import requests
from ..utils import globals
from .ApiModels.Element import Element
from typing import Type, TypeVar, List

T = TypeVar("T", bound="CommonElement")

def query(cls: Type[T], query_input: dict) -> List[T]:
    host = f"{globals.get_host()}/projects/{globals.get_project_id()}/query-results"
    elements =[]
    try:
        logging.debug(f"Sending query to {host} with input: {query_input}")
        response = requests.post(host, json=query_input)
        response.raise_for_status()
        data = response.json()
        logging.debug(f"Query Response Data: {data}")

        elements = [cls.fromDict(elem) for elem in data]
    except Exception as e:
        logging.error(f"Error during query: {e}")
        logging.error(response.json())
    return elements
def queryAnyByIds(element_ids: List[str],select: List[str],cls:Type[T]) -> List[T]:
    query_input = {
            '@type':'Query',
            'select': ['name','@id','@type','owner']+select,
            'where': {
                '@type': 'CompositeConstraint',
                'operator': 'or',
                'constraint': [
                    {
                        '@type': 'PrimitiveConstraint',
                        'inverse': False,
                        'operator': '=',
                        'property': '@id',
                        'value': [element_id]
                    } for element_id in element_ids
                ]
            }
            }
    response:list[T] = query(cls,query_input)
    return response

def queryAnyByIdsByType(element_ids: list[str], select: list[str], cls: Type[T], apiType: str) -> list[T]:
    if not element_ids:
        return []

    query_input = {
        '@type': 'Query',
        'select': ['name', '@id', '@type', 'owner'] + select,
        'where': {
            '@type': 'CompositeConstraint',
            'operator': 'and',
            'constraint': [
                {
                    '@type': 'PrimitiveConstraint',
                    'operator': '=',
                    'property': '@type',
                    'value': [apiType]
                },
                {
                    '@type': 'CompositeConstraint',
                    'operator': 'or',
                    'constraint': [
                        {
                            '@type': 'PrimitiveConstraint',
                            'operator': '=',
                            'property': '@id',
                            'value': [element_id]
                        } for element_id in element_ids
                    ]
                }
            ]
        }
    }
    
    response: list[T] = query(cls, query_input)
    return response
def queryElementsByIds(element_ids: List[str],select: List[str]) -> List[Element]:
    return queryAnyByIds(element_ids,select,Element)
    

def queryByType(select: List[str], cls: Type[T], apiType: str) -> List[T]:
    query_input = {
        '@type': 'Query',
        'select': ['name', '@id', '@type', 'owner'] + select,
        'where': {
            '@type': 'PrimitiveConstraint',
            'operator': '=',
            'property': '@type',
            'value': [apiType]
        }
    }
    
    response: List[T] = query(cls, query_input)
    return response