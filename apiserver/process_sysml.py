import os
import sys
import re
import time
from jupyter_client import BlockingKernelClient

def run_task():
    print("DEBUG: Skript im Container gestartet", file=sys.stderr)
    
    runtime_dir = "/home/sysml/.local/share/jupyter/runtime"
    try:
        conn_files = [os.path.join(runtime_dir, f) for f in os.listdir(runtime_dir) if f.startswith("kernel-")]
        if not conn_files:
            print("ERROR: Keine kernel-*.json gefunden!", file=sys.stderr)
            return
        conn_file = max(conn_files, key=os.path.getmtime)
        print(f"DEBUG: Nutze Connection File: {conn_file}", file=sys.stderr)
    except Exception as e:
        print(f"ERROR beim Dateizugriff: {e}", file=sys.stderr)
        return

    client = BlockingKernelClient()
    client.load_connection_file(conn_file)
    client.start_channels()


    client.kernel_info() 
    try:
        client.get_shell_msg(timeout=30)
        print("Kernel-Verbindung steht (Java-Loop aktiv).")
    except:
        print("Warte auf Kernel-Initialisierung (Timeout)...", file=sys.stderr)

    project_id = os.environ.get("PROJECT_ID", "")
    project_name = os.environ.get("PUBLISH_GUID", "DefaultProject")
    sysml_content = os.environ.get("SYSML_CONTENT", "")
    safe_name = project_name.replace("-", "_").replace(" ", "_")
    
    commands = []
    if project_id:
        commands.append(f'%load --id "{project_id}"')
    commands.append(f'package {safe_name} {{\n{sysml_content}\n}}')
    commands.append(f'%publish -d --project={project_name} {safe_name}')

    print(f"DEBUG: Send {len(commands)} commands Kernel...", file=sys.stderr)

    last_final_id = None 

    for i, cmd in enumerate(commands):
        print(f"DEBUG Sende Befehl an Kernel: {cmd[:50]}...", file=sys.stderr)
        msg_id = client.execute(cmd)
        finished = False
        start_time = time.time()
        while not finished:
            try:
                msg = client.get_iopub_msg(timeout=30) 
                msg_type = msg['header']['msg_type']
                content = msg.get("content", {})

                if msg_type == 'stream' and 'text' in content:
                    print(content['text'], end="", flush=True)

                if "data" in content and "text/plain" in content["data"]:
                    data = content["data"]["text/plain"]
                    if i == len(commands) - 1:
                        getSavedText = data.split("Saved to Project")
                        if len(getSavedText) <= 1:
                            raise Exception("Konnte Projekt-ID nicht extrahieren.")
                        
                        openParent = getSavedText[1].split("(")
                        projectIdText = openParent[1].split(")")[0]
                        last_final_id = projectIdText.strip()


                if msg_type == 'status' and content.get('execution_state') == 'idle':
                    if msg.get('parent_header', {}).get('msg_id') == msg_id:
                        finished = True

                if time.time() - start_time > 300:
                    print("ERROR: Timeout", file=sys.stderr)
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
