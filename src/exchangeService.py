import os
import logging
import subprocess
import sys
from unittest import result
import src.utils.globals as globals
from src.utils.docker_env import DockerEnvironment

class ExchangeService:
    PROJECT_STRING_KEY_ID = "Model ID:"

    def __init__(self,upload_script_path:str,file_path:str):
        self.upload_script_path = upload_script_path
        self.file_path = file_path

    def read_sysml_files(self):
        res = []
        for files in os.listdir(self.file_path):
            if files.endswith(".sysml"):
               res.append(os.path.join(self.file_path, files))
        return res
    
    def sendToApi(self, publish_guid:str, data:list):
        with DockerEnvironment() as env:
            logging.info("Uploading SysML files to the API...")
            project_id = env.send_sysml(publish_guid, [globals.PROJECT_ID if globals.PROJECT_ID is not None else ""], data)
            
            return project_id
    
  
