
import logging
import os
from .Repository import Repository
import json
HOST = "http://localhost:9000"
PROJECT_ID = None
LAST_COMMIT_ID = None
DATABASE = None
PUBLISH_GUID = None
OUTPUT_FOLDER = None

def set_output_folder(folder_path:str)->str:
    global OUTPUT_FOLDER
    OUTPUT_FOLDER = folder_path
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    return OUTPUT_FOLDER

def initPublishGuid() -> str:
    global PUBLISH_GUID, PROJECT_ID
    meta_path = os.path.join(OUTPUT_FOLDER, "meta.json")
    
    try:
        with open(meta_path, "r") as f:
            meta = json.load(f)
            PUBLISH_GUID = meta.get("publish_guid")
            PROJECT_ID = meta.get("project_id")
    except (FileNotFoundError, json.JSONDecodeError):
        PUBLISH_GUID = None
        PROJECT_ID = None

    if PUBLISH_GUID is None:
        import uuid
        PUBLISH_GUID = f"Publish{str(uuid.uuid4())}"
        meta = {"publish_guid": PUBLISH_GUID}
        
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=4)
            f.flush()
            os.fsync(f.fileno())

def get_publish_guid()->str:
    global PUBLISH_GUID
    if PUBLISH_GUID is None:
        logging.error("Publish GUID not set. Please initialize the publish GUID first.")
        raise Exception("Publish GUID not set. Please initialize the publish GUID first.")
    return PUBLISH_GUID
    
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

def save_meta_data():

    global OUTPUT_FOLDER
    global PUBLISH_GUID
    global PROJECT_ID

    meta = {
        "publish_guid": PUBLISH_GUID,
        "project_id": PROJECT_ID
    }
    
    if OUTPUT_FOLDER is None:
        logging.error("Output folder not set. Please set the output folder first.")
        raise Exception("Output folder not set. Please set the output folder first.")
    with open(os.path.join(OUTPUT_FOLDER, "meta.json"), "w") as f:
        json.dump(meta, f, indent=4)