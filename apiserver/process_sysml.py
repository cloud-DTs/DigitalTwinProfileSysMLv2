import logging
import os
import sys
import re
import time
from jupyter_client import BlockingKernelClient

def run_task():
    logging.debug("DEBUG: Script started in container")
    
    runtime_dir = "/home/sysml/.local/share/jupyter/runtime"
    try:
        conn_files = [os.path.join(runtime_dir, f) for f in os.listdir(runtime_dir) if f.startswith("kernel-")]
        if not conn_files:
            logging.error("No kernel-*.json found!")
            return
        conn_file = max(conn_files, key=os.path.getmtime)
        logging.debug(f"Using connection file: {conn_file}")
    except Exception as e:
        logging.error(f"ERROR accessing files: {e}")
        return

    client = BlockingKernelClient()
    client.load_connection_file(conn_file)
    client.start_channels()


    client.kernel_info() 
    try:
        client.get_shell_msg(timeout=30)
        logging.debug("Kernel connection established (Java loop active).")
    except:
        logging.debug("wait for kernel initialization (timeout)...")

    project_id = os.environ.get("PROJECT_ID", "")
    project_name = os.environ.get("PUBLISH_GUID", "DefaultProject")
    sysml_content = os.environ.get("SYSML_CONTENT", "")
    safe_name = project_name.replace("-", "_").replace(" ", "_")
    
    commands = []
    if project_id:
        commands.append(f'%load --id "{project_id}"')
    commands.append(f'package {safe_name} {{\n{sysml_content}\n}}')
    commands.append(f'%publish -d --project={project_name} {safe_name}')

    logging.debug(f"Send {len(commands)} commands Kernel...")

    last_final_id = None 

    for i, cmd in enumerate(commands):
        logging.debug(f"Send command to kernel: {cmd[:50]}...")
        msg_id = client.execute(cmd)
        finished = False
        start_time = time.time()
        while not finished:
            try:
                msg = client.get_iopub_msg(timeout=30) 
                msg_type = msg['header']['msg_type']
                content = msg.get("content", {})

                if msg_type == 'stream' and 'text' in content:
                    logging.debug(content['text'])

                if "data" in content and "text/plain" in content["data"]:
                    data = content["data"]["text/plain"]
                    if i == len(commands) - 1:
                        getSavedText = data.split("Saved to Project")
                        if len(getSavedText) <= 1:
                            raise Exception("cant extract project id from kernel output")
                        
                        openParent = getSavedText[1].split("(")
                        projectIdText = openParent[1].split(")")[0]
                        last_final_id = projectIdText.strip()


                if msg_type == 'status' and content.get('execution_state') == 'idle':
                    if msg.get('parent_header', {}).get('msg_id') == msg_id:
                        finished = True

                if time.time() - start_time > 300:
                    logging.error("Timeout")
                    finished = True

            except Exception as e:
                time.sleep(1)

    if last_final_id:
        print(f"\nModel ID: {last_final_id}")
    else:
        print("\nModel ID: NOT_FOUND")

    client.stop_channels()

if __name__ == "__main__":
    run_task()
