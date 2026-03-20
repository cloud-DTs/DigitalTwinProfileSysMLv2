from datetime import date
import sys
from src.TargetModel.twin import Twin
import src.utils.globals as globals
import logging
from src.parser import Parser
import os
from src.exchangeService import ExchangeService
import src.api.project as project_api
import src.api.commit as commit_api
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
upload_script = os.path.join(BASE_DIR, "uploadSysml.sh")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

def args_check():
    if len(sys.argv) < 2:
        logging.error("Usage: python main.py <path_to_sysml_directory>")
        sys.exit(1)
    filepath = sys.argv[1]
    if filepath == None:
        logging.error("Please provide the path to the directory containing .sysml files.")
        sys.exit(1)

    output_folder = sys.argv[2] if len(sys.argv) > 2 else "output"
    globals.set_output_folder(output_folder)
    return filepath
def remove_none_values(data):
    if isinstance(data, list):
        return [v for v in (remove_none_values(item) for item in data) 
                if v is not None and v != "" and v != "None"]
    
    elif isinstance(data, dict):
        clean_dict = {}
        for key, value in data.items():
            recursive_value = remove_none_values(value)
            if (recursive_value is not None and 
                recursive_value != "" and 
                recursive_value != "None" and 
                recursive_value != {}):
                clean_dict[key] = recursive_value
        return clean_dict if clean_dict else None
    
    else:
        if data == "None" or data is None:
            return None
        return data

def setup(projectId:str):
    logging.info("Setting up the environment...")
    globals.set_project(projectId)
    globals.set_last_commit_id(commit_api.get_last_commit(projectId).id)

def parseSysmlToTwinClass(sysmlDirPath:str, outputFolder="output")->list[Twin]:
    filepath = sysmlDirPath
    outputFolder = outputFolder
    globals.set_output_folder(outputFolder)
    globals.initPublishGuid()
    publiush_guid = globals.get_publish_guid()
    exchangeService = ExchangeService(upload_script_path=upload_script, file_path=filepath)
    sysml_files = exchangeService.read_sysml_files()
    if not sysml_files:
        logging.error("No .sysml files found in the provided directory.")
        return
    projectId = exchangeService.sendToApi(publiush_guid, sysml_files)
    setup(projectId)
    globals.save_meta_data()
    logging.info("Environment setup complete.")

    logging.info("Starting parsing process...")
    globals.initDataBase()
    
    parser = Parser()
    return parser.parse()
    


    
def main():
    filepath = args_check()
    twins = parseSysmlToTwinClass(filepath)
    for twin in twins:
        if len(twin.name) > 10:
            logging.warning(f"Twin Model name '{twin.name}' is longer than 10 characters and will not be considered")
            continue
        logging.info(f"Generated Twin Model: {twin.name}")
        output_files = [
            ("config", twin.to_config_dict()),
            ("config_hierarchy", twin.to_hierarchy_dict()),
            ("config_events", twin.to_event_dict()),
            ("config_iot_devices", twin.to_iot_device_dict())
        ]

        dir_path = f"output/{twin.name}/"
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        for filename, content in output_files:
            clean_content = remove_none_values(content)
            
            with open(os.path.join(dir_path, f"{filename}.json"), "w") as f:
                import json
                json.dump(clean_content, f, indent=4)

    
if __name__ == "__main__":
    main()