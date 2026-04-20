import os
import logging
import subprocess
import sys

EXPORT_PATH_KEY = "Export Path:"
CONTAINER_NAME = "sysml-kernel-container"

class ExchangeService:
    def __init__(self, upload_script_path: str, file_path: str):
        self.upload_script_path = upload_script_path
        self.file_path = file_path

    def read_sysml_files(self):
        return [
            os.path.join(self.file_path, f)
            for f in os.listdir(self.file_path)
            if f.endswith(".sysml")
        ]

    def sendToApi(self, data: list) -> str:
        logging.info("Uploading SysML files to the API...")
        print(f">> Uploading files: {data}", flush=True)
        result = subprocess.run(
    ['sh', self.upload_script_path] + data,
    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    stdin=subprocess.DEVNULL,
    text=True
)
        if result.returncode != 0:
            logging.error("STDOUT: %s", result.stdout)
            logging.error("STDERR: %s", result.stderr)
            sys.exit(1)

        logging.info("Full STDOUT: %s", result.stdout)

        export_line = next((l for l in result.stdout.splitlines() if "Export path:" in l), None)
        if not export_line:
            logging.error("Export Path not found in output")
            sys.exit(1)

        container_path = export_line.split(":", 1)[1].strip()
        local_path = os.path.join(os.path.dirname(self.upload_script_path), "export.json")

        cp_result = subprocess.run(
            ["docker", "cp", f"{CONTAINER_NAME}:{container_path}", local_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if cp_result.returncode != 0:
            logging.error("docker cp failed: %s", cp_result.stderr)
            sys.exit(1)

        logging.info(f"Export saved to: {local_path}")
        return local_path