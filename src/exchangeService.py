import os
import logging
import subprocess
import sys
from unittest import result
import src.utils.globals as globals

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


        logging.info("Uploading SysML files to the API...")

        result = subprocess.run(['sh',f"{self.upload_script_path}"]+[publish_guid]+[globals.PROJECT_ID if globals.PROJECT_ID is not None else ""]+data,stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            logging.error("Error occurred during upload.")
            logging.error("STDOUT: %s", result.stdout)
            logging.error("STDERR: %s", result.stderr)
            sys.exit(1)
            return

        logging.info("Full STDOUT: %s", result.stdout)
        projectId = [line for line in result.stdout.splitlines() if line.startswith(self.PROJECT_STRING_KEY_ID)][0].split(":")[1].strip()
        logging.info("Upload complete.")
        logging.info(f"Project ID: {projectId}")
        logging.info(f"Project Name: {globals.PUBLISH_GUID}")
        logging.info("Full STDOUT: %s", result.stdout)
        return projectId
    
  
