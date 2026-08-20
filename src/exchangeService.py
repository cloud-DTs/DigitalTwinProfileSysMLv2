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
        subprocess.run(
            [
                "docker",
                "exec",
                CONTAINER_NAME,
                "rm",
                "-f",
                "/home/sysml/export.json"
            ],
            check=True
        )
        logging.info("Processing SysML files...")
        print(f">> SysML files: {data}", flush=True)

        process = subprocess.Popen(
            ['sh', self.upload_script_path] + data,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            text=True,
            bufsize=1
        )

        lines = []

        for line in process.stdout:
            print(line, end="", flush=True)
            lines.append(line)

        returncode = process.wait()

        if returncode != 0:
            raise RuntimeError(
                f"SysML processing failed with exit code {returncode}"
            )

        output = "".join(lines)

        export_line = next(
            (l for l in output.splitlines() if "Export path:" in l),
            None
        )

        if not export_line:
            raise RuntimeError("Export Path not found in SysML converter output")

        container_path = export_line.split(":", 1)[1].strip()

        local_path = os.path.join(
            os.path.dirname(self.upload_script_path),
            "export.json"
        )

        cp_result = subprocess.run(
            [
                "docker",
                "cp",
                f"{CONTAINER_NAME}:{container_path}",
                local_path
            ]
        )

        if cp_result.returncode != 0:
            raise RuntimeError("docker cp failed")

        cleanup_result = subprocess.run(
            [
                "docker",
                "exec",
                CONTAINER_NAME,
                "rm",
                "-f",
                container_path,
            ]
        )

        if cleanup_result.returncode != 0:
            logging.warning(
                f"Could not delete container export: {container_path}"
            )

        logging.info(f"Export saved to: {local_path}")
        return local_path
