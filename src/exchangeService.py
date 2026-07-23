import os
import logging
import re
import subprocess
import sys

EXPORT_PATH_KEY = "Export Path:"
CONTAINER_NAME = "sysml-kernel-container"

# The kernel reports positions against the single buffer it was handed, e.g.
# "(11.sysml line : 190 column : 31)" -- where "11" is the kernel's cell counter,
# not one of our files.
KERNEL_POSITION_RE = re.compile(r"\(\d+\.sysml line : (\d+) column : (\d+)\)")

# process_sysml.py prepends "package GeneratedExport {" before the concatenated files.
WRAPPER_LINE_OFFSET = 1

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

    def _build_line_spans(self, data: list):
        """Map each file onto the line range it occupies in the buffer sent to the kernel.

        The files are concatenated in argv order (see uploadSysml.sh), so a file's span is
        just the running line total. Returns [(first_line, last_line, path), ...].
        """
        spans = []
        offset = WRAPPER_LINE_OFFSET
        for path in data:
            try:
                with open(path, encoding="utf-8") as f:
                    line_count = len(f.read().splitlines())
            except OSError as e:
                logging.warning("Could not measure %s for error mapping: %s", path, e)
                return []
            spans.append((offset + 1, offset + line_count, path))
            offset += line_count
        return spans

    def _localize(self, line: str, spans: list) -> str:
        """Rewrite kernel buffer positions into 'file.sysml line : N' of the original file."""
        def replace(match):
            buffer_line, column = int(match.group(1)), match.group(2)
            for first, last, path in spans:
                if first <= buffer_line <= last:
                    local_line = buffer_line - first + 1
                    return f"({os.path.basename(path)} line : {local_line} column : {column})"
            return match.group(0)

        return KERNEL_POSITION_RE.sub(replace, line)

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
            spans = self._build_line_spans(data)
            print("\n--- SysML Conversion Errors ---", flush=True)
            for line in error_lines:
                print(self._localize(line, spans), flush=True)
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