import sys
import src.utils.globals as globals
import logging
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
    return filepath

def setup(projectId:str):
    logging.info("Setting up the environment...")
    globals.set_project(projectId)
    globals.set_last_commit_id(commit_api.get_last_commit(projectId).id)
def main():
    filepath = args_check()
    exchangeService = ExchangeService(upload_script_path=upload_script, file_path=filepath)
    sysml_files = exchangeService.read_sysml_files()
    if not sysml_files:
        logging.error("No .sysml files found in the provided directory.")
        return
    projectId = exchangeService.sendToApi(sysml_files)
    setup(projectId)
    logging.info("Environment setup complete.")

    logging.info("Starting parsing process...")
    globals.initDataBase()
    from src.parser import Parser
    parser = Parser()
    parser.parse()

    


if __name__ == "__main__":
    main()