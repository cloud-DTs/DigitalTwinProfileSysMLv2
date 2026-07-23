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
        error_lines = [l for l in result.stdout.splitlines()
                       if l.startswith("ERROR") or l.startswith("WARNING") or l.startswith("  |")]
        if error_lines:
            print("\n--- SysML Conversion Errors ---", flush=True)
            for line in error_lines:
                print(line, flush=True)
            print("--- End SysML Conversion Errors ---\n", flush=True)

        if result.returncode != 0:
            if result.stderr.strip():
                logging.error("STDERR: %s", result.stderr)
            raise RuntimeError(
                f"SysML conversion failed. See errors above. "
                f"(exit code {result.returncode})"
            )

        logging.info("Full STDOUT: %s", result.stdout)

        export_line = next((l for l in result.stdout.splitlines() if "Export path:" in l), None)
        if not export_line:
            logging.error("Export Path not found in container output")
            raise RuntimeError(
                "SysML conversion produced no export. The SysML file(s) likely contain errors."
            )

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