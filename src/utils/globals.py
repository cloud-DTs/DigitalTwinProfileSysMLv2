
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
