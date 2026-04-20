from jupyter_client import BlockingKernelClient
import os, time, base64, re

runtime_dir = "/home/sysml/.local/share/jupyter/runtime"
conn_files = [os.path.join(runtime_dir, f) for f in os.listdir(runtime_dir) if f.startswith("kernel-")]
conn_file = max(conn_files, key=os.path.getmtime)

client = BlockingKernelClient()
client.load_connection_file(conn_file)
client.start_channels()

EXPORT_PATH = "/home/sysml/export.json"

def run_cmd(cmd, timeout=600):
    msg_id = client.execute(cmd)
    while True:
        msg = client.get_iopub_msg(timeout=timeout)
        if msg["header"]["msg_type"] in ("execute_result", "display_data"):
            data = msg["content"].get("data", {})
            html = data.get("text/html", "")
            match = re.search(r'base64,([^"]+)"', html)
            if match:
                decoded = base64.b64decode(match.group(1)).decode("utf-8")
                with open(EXPORT_PATH, "w") as f:
                    f.write(decoded)
                print(">> Export saved", flush=True)
        if msg["header"]["msg_type"] == "error":
            print(f"ERROR: {msg['content']['ename']}: {msg['content']['evalue']}", flush=True)
        if (msg["header"]["msg_type"] == "status"
                and msg["content"].get("execution_state") == "idle"
                and msg["parent_header"].get("msg_id") == msg_id):
            break

def run_task():
    raw_content = os.environ.get("SYSML_CONTENT", "")
    
    safe_name = "GeneratedExport"

    print(f">> Generate Export Container: {safe_name}", flush=True)
    t1 = time.time()
    
    wrapped_content = f"package {safe_name} {{\n{raw_content}\n}}"
    run_cmd(wrapped_content)

    print("Load Model")
    print(f">> Export package '{safe_name}'...", flush=True)
    t2 = time.time()
    run_cmd(f"%export {safe_name}")
    print(f">> Export finished" ,flush=True)

    if os.path.exists(EXPORT_PATH):
        print(f"\nExport path: {EXPORT_PATH}", flush=True)
    else:
        print("\nExport path: NOT_FOUND (Check Kernel Logs)", flush=True)
if __name__ == "__main__":
    run_task()
    os._exit(0)