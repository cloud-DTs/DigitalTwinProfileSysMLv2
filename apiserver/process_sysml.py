#!/usr/bin/env python3
import os
import nbformat
from nbformat.v4 import new_notebook, new_code_cell
from pathlib import Path
import subprocess
import uuid
import re
import sys

publishguid = "Publish" + str(uuid.uuid4()).replace("-", "")
notebook_path = Path("/home/sysml/publish_notebook.ipynb")


sysml_content = os.environ.get("SYSML_CONTENT", "")
dtLib = None
metaLib = None
with open("/home/sysml/DigitalTwinLibrary.sysml", "r") as f:
    dtLib = f.read()

with open("/home/sysml/MetaLibrary.sysml", "r") as f:
    metaLib = f.read()


cell1_content = f"""
package {publishguid} {{
{sysml_content}
}}
"""
cell2_content = f"%publish {publishguid}"

nb = new_notebook(
    cells=[
        new_code_cell(dtLib),
        new_code_cell(metaLib),
        new_code_cell(cell1_content),
        new_code_cell(cell2_content)
    ],
    metadata={
        "kernelspec": {
            "name": "sysml",
            "display_name": "SysML Kernel",
            "language": "python"
        }
    }
)

with open(notebook_path, "w") as f:
    nbformat.write(nb, f)

try:
    result = subprocess.run([
        "jupyter", "nbconvert",
        "--to", "notebook",
        "--execute",
        "--inplace",
        str(notebook_path)
    ], check=True, capture_output=True, text=True)

except subprocess.CalledProcessError as e:
    print("stdout:", e.stdout)
    print("stderr:", e.stderr)
    sys.exit(1)

subprocess.run(["cat", str(notebook_path)])
nb_executed = nbformat.read(notebook_path, as_version=4)

for i, cell in enumerate(nb_executed.cells):
    if "outputs" in cell:
        print(f"\n--- Cell {i+1} outputs ---")
        for output in cell["outputs"]:
            if "text" in output:
                text = "".join(output["text"])
             
            elif "data" in output:
                if (i == nb_executed.cells.__len__() - 1):
                    if "Saved to Project" in output["data"].get("text/plain", ""):
                        print("Model successfully published.")
                        res = output["data"]["text/plain"]
                        match = res.split("(")[1]
                        match = match.split(")")[0]
                        model_id = match.strip()
                        print(f"Model ID: {model_id}")
                    else:
                        print("Error during publishing. Something is wrong in your SysML syntax")
                        sys.exit(1)
                print(output["data"].get("text/plain", ""))


