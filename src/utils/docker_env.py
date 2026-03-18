import docker
import requests
import time
import os
import secrets

DEFAULT_ENV = {
    "POSTGRES_USER":           "sysml_admin",
    "POSTGRES_DB":             "sysml2",
    "DB_SERVER_URL":           "jdbc:postgresql://postgresdbserver:5432/sysml2",
    "API_SYSML_API_SERVER_URL":"sysmlapiserver:9000",
    "API_RELEASE":             "2025-02",
    "SYSML_API_SERVER":        "sysmlapiserver",
}
class DockerEnvironment:
    
    def __init__(self, host="http://localhost:9000",env: dict = None):
        self.client = docker.from_env()
        self.host = host
        self.network_name = "sysml-network"
        password = (env or {}).get("POSTGRES_PASSWORD") or secrets.token_urlsafe(16)
        self.env = {
            **self.DEFAULT_ENV,
            "POSTGRES_PASSWORD": password,
            **(env or {})
        }

    def __enter__(self):
        self._ensure_network()
        self._start_postgres()
        self._start_api()
        self._start_kernel()
        self._wait_for_api()
        return self

    def _ensure_network(self):
        try:
            self.client.networks.get(self.network_name)
        except:
            self.client.networks.create(self.network_name)

    def _start_postgres(self):
        self.client.containers.run(
            "postgres:9.6.6",
            name="sysml-postgres",
            environment={
                "POSTGRES_USER": os.getenv("POSTGRES_USER", "sysml"),
                "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD", "sysml"),
                "POSTGRES_DB": os.getenv("POSTGRES_DB", "sysml")
            },
            network=self.network_name,
            detach=True,
            remove=True
        )

    def _start_api(self):
        self.client.containers.run(
            "ghcr.io/cloud-dts/sysml-api:latest",
            name="sysmlapiserver",
            ports={"9000/tcp": 9000},
            network=self.network_name,
            detach=True,
            remove=True
        )

    def _start_kernel(self):
        self.client.containers.run(
            "ghcr.io/cloud-dts/sysml-jupyter:latest",
            name="sysml-kernel-container",
            environment={"SYSML_API_SERVER": "http://sysmlapiserver:9000"},
            ports={"8888/tcp": 8888},
            network=self.network_name,
            command="conda run --no-capture-output -n sysml jupyter kernel --kernel=sysml --ip=0.0.0.0",
            detach=True,
            remove=True
        )

    def _wait_for_api(self):
        print("Waiting for API...")
        for _ in range(30):
            try:
                requests.get(self.host)
                print("✓ API ready")
                return
            except:
                time.sleep(2)
        raise Exception("API did not start")

    def send_sysml(self, publish_guid: str, project_id: str, file_paths: list[str]) -> str:
    
        sysml_content = ""
        for path in file_paths:
            with open(path, "r") as f:
                sysml_content += f.read() + "\n"

        
        container = self.client.containers.get("sysml-kernel-container")
        result = container.exec_run(
            cmd=["conda", "run", "-n", "sysml", "python", "/home/sysml/process_sysml.py"],
            environment={
                "SYSML_CONTENT": sysml_content,
                "PUBLISH_GUID": publish_guid,
                "PROJECT_ID": project_id or ""
            }
        )

        output = result.output.decode("utf-8")
        for line in output.splitlines():
            if line.startswith("Model ID:"):
                return line.split(":")[1].strip()
        raise Exception("Could not extract project ID")

    def __exit__(self, *args):
        for name in ["sysml-kernel-container", "sysmlapiserver", "sysml-postgres"]:
            try:
                self.client.containers.get(name).stop()
                print(f"✓ Stopped {name}")
            except:
                pass
        try:
            self.client.networks.get(self.network_name).remove()
        except:
            pass