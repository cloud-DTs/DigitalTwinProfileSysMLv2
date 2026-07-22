from jupyter_client import BlockingKernelClient
import os, time, base64, re, sys

runtime_dir = "/home/sysml/.local/share/jupyter/runtime"
conn_files = [os.path.join(runtime_dir, f) for f in os.listdir(runtime_dir) if f.startswith("kernel-")]
conn_file = max(conn_files, key=os.path.getmtime)

client = BlockingKernelClient()
client.load_connection_file(conn_file)
client.start_channels()

EXPORT_PATH = "/home/sysml/export.json"

ANSI_ESCAPE_RE = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')

def strip_ansi(text):
    return ANSI_ESCAPE_RE.sub("", text)

def run_cmd(cmd, timeout=600):
    errors = []
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
            ename = strip_ansi(msg['content']['ename'])
            evalue = strip_ansi(msg['content']['evalue'])
            traceback_lines = [strip_ansi(line) for line in msg['content'].get('traceback', [])]
            error_msg = f"{ename}: {evalue}"
            errors.append(error_msg)
            print(f"ERROR: {error_msg}", flush=True)
            for tb_line in traceback_lines:
                print(f"  {tb_line}", flush=True)
        if (msg["header"]["msg_type"] == "status"
                and msg["content"].get("execution_state") == "idle"
                and msg["parent_header"].get("msg_id") == msg_id):
            break
    return errors

def run_task():
    raw_content = os.environ.get("SYSML_CONTENT", "")

    safe_name = "GeneratedExport"

    print(f">> Generate Export Container: {safe_name}", flush=True)
    t1 = time.time()

    wrapped_content = f"package {safe_name} {{\n{raw_content}\n}}"
    errors = run_cmd(wrapped_content)
    if errors:
        print("\nERROR_SUMMARY: SysML parsing failed", flush=True)
        for e in errors:
            print(f"  | {e}", flush=True)
        sys.exit(1)

    print("Load Model")
    print(f">> Export package '{safe_name}'...", flush=True)
    t2 = time.time()
    export_errors = run_cmd(f"%export {safe_name}")
    if export_errors:
        print("\nERROR_SUMMARY: Export failed", flush=True)
        for e in export_errors:
            print(f"  | {e}", flush=True)
        sys.exit(1)
    print(f">> Export finished" ,flush=True)

    if os.path.exists(EXPORT_PATH):
        print(f"\nExport path: {EXPORT_PATH}", flush=True)
    else:
        print("\nExport path: NOT_FOUND (Check Kernel Logs)", flush=True)
if __name__ == "__main__":
    run_task()
    os._exit(0)