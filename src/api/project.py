from .ApiModels.Project import Project
import requests
import logging
from ..utils import globals

def get_project_by_id(project_id:str)->Project:
    logging.info(f"Fetching project with ID: {project_id} from host: {globals.get_host()}")
    try:
        response = requests.get(f"{globals.get_host()}/projects/{project_id}")
        response.raise_for_status()
    except Exception as e:
        logging.error(f"Error fetching project: {e}")
        

    project_data = response.json()
    project = Project.fromDict(project_data)
    return project