import sys
import os
import time
import base64
import re

from jupyter_client import BlockingKernelClient


runtime_dir = "/home/sysml/.local/share/jupyter/runtime"

conn_files = [
    os.path.join(runtime_dir, f)
    for f in os.listdir(runtime_dir)
    if f.startswith("kernel-")
]

if not conn_files:
    raise RuntimeError(
        f"No Jupyter kernel connection file found in {runtime_dir}"
    )

conn_file = max(conn_files, key=os.path.getmtime)

print(f">> Using kernel connection: {conn_file}", flush=True)

client = BlockingKernelClient()
client.load_connection_file(conn_file)
client.start_channels()

EXPORT_PATH = "/home/sysml/export.json"


def run_cmd(cmd, timeout=3600):
    print(f">> Executing command: {cmd}", flush=True)

    msg_id = client.execute(cmd)
    kernel_errors = []

    while True:
        msg = client.get_iopub_msg(timeout=timeout)

        msg_type = msg["header"]["msg_type"]
        parent_msg_id = msg.get("parent_header", {}).get("msg_id")

        if parent_msg_id and parent_msg_id != msg_id:
            continue

        if msg_type in ("execute_result", "display_data"):
            data = msg["content"].get("data", {})

            print(
                f">> Jupyter output type={msg_type}, "
                f"mime_types={list(data.keys())}",
                flush=True,
            )

            text = data.get("text/plain", "")

            if text:
                print(">> KERNEL RESPONSE BEGIN", flush=True)
                print(text, flush=True)
                print(">> KERNEL RESPONSE END", flush=True)

                if "ERROR:" in text or "WARNING:" in text:
                    kernel_errors.append(text.strip())

            html = data.get("text/html", "")

            if html:
                print(
                    f">> text/html length: {len(html)}",
                    flush=True,
                )

                match = re.search(r'base64,([^"]+)"', html)

                if match:
                    decoded = base64.b64decode(match.group(1))

                    with open(EXPORT_PATH, "wb") as f:
                        f.write(decoded)

                    print(
                        f">> Export saved: {EXPORT_PATH} "
                        f"({len(decoded)} bytes)",
                        flush=True,
                    )

        elif msg_type == "stream":
            content = msg.get("content", {})
            stream_name = content.get("name", "")
            stream_text = content.get("text", "")

            print(
                f">> KERNEL STREAM [{stream_name}]:",
                flush=True,
            )
            print(stream_text, end="", flush=True)

            if stream_name == "stderr" and (
                "ERROR:" in stream_text
                or "WARNING:" in stream_text
            ):
                kernel_errors.append(stream_text.strip())

        elif msg_type == "error":
            content = msg["content"]

            ename = content.get("ename", "UnknownError")
            evalue = content.get("evalue", "")

            raise RuntimeError(
                f"SysML kernel error: {ename}: {evalue}"
            )

        elif msg_type == "status":
            if (
                msg["content"].get("execution_state") == "idle"
                and parent_msg_id == msg_id
            ):
                break

    if kernel_errors:
        raise RuntimeError(
            "SysML validation failed:\n"
            + "\n".join(kernel_errors)
        )

    print(">> Kernel execution finished (idle)", flush=True)


def run_task():
    raw_content = sys.stdin.read()

    if not raw_content.strip():
        raise RuntimeError(
            "No SysML content received on stdin"
        )

    safe_name = "GeneratedExport"

    print(
        f">> Generate Export Container: {safe_name}",
        flush=True,
    )

    t1 = time.time()

    wrapped_content = (
        f"package {safe_name} {{\n"
        f"{raw_content}\n"
        f"}}"
    )

    run_cmd(wrapped_content)

    print(
        f">> Model load finished after "
        f"{time.time() - t1:.2f}s",
        flush=True,
    )

    print("Load Model", flush=True)

    if os.path.exists(EXPORT_PATH):
        print(
            f">> Removing stale export: {EXPORT_PATH}",
            flush=True,
        )
        os.remove(EXPORT_PATH)

    print(
        f">> Export package '{safe_name}'...",
        flush=True,
    )

    t2 = time.time()

    run_cmd(f"%export {safe_name}")

    print(
        f">> %export command finished after "
        f"{time.time() - t2:.2f}s",
        flush=True,
    )

    if not os.path.exists(EXPORT_PATH):
        raise RuntimeError(
            f"SysML export failed: "
            f"{EXPORT_PATH} was not created"
        )

    export_size = os.path.getsize(EXPORT_PATH)

    if export_size == 0:
        raise RuntimeError(
            f"SysML export failed: "
            f"{EXPORT_PATH} is empty"
        )

    print(">> Export finished", flush=True)

    print(
        f">> Export size: {export_size} bytes",
        flush=True,
    )

    print(
        f"\nExport path: {EXPORT_PATH}",
        flush=True,
    )


if __name__ == "__main__":
    try:
        run_task()

    except Exception as e:
        print(
            f"FATAL: {type(e).__name__}: {e}",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(1)

    finally:
        try:
            client.stop_channels()
        except Exception:
            pass