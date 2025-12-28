
import logging
from .Repository import Repository
HOST = "http://localhost:9000"
PROJECT_ID = None
LAST_COMMIT_ID = None
DATABASE = None    
def get_project_id() -> str:
    global PROJECT_ID
    if PROJECT_ID is None:
        logging.error("Project not set. Please set the project ID first.")
        raise Exception("Project not set. Please set the project ID first.")
    return PROJECT_ID

def set_project(project_id) -> str:
    global PROJECT_ID
    PROJECT_ID = project_id

def get_host() -> str:
    global HOST
    return HOST

def set_host(host:str) -> str:
    global HOST
    HOST = host

def get_last_commit_id() -> str:
    global LAST_COMMIT_ID
    return LAST_COMMIT_ID

def set_last_commit_id(commit_id:str) -> str:
    global LAST_COMMIT_ID
    LAST_COMMIT_ID = commit_id

def initDataBase()->Repository:
    global DATABASE
    DATABASE = Repository()
    return DATABASE

def get_database()->Repository:
    global DATABASE
    if DATABASE is None:
        logging.error("Database not initialized. Please initialize the database first.")
        raise Exception("Database not initialized. Please initialize the database first.")
    return DATABASE