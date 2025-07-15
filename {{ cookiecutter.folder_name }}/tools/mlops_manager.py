import os
import platform
import socket
import subprocess
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path

import psutil

import typer
from typing import List, Optional, Literal


class MlopsManager:
    def __init__(self, action=None, service=None, cache=False, jupyter_port=8895, delete_volume=False, docker_build=False):
        self.action = action
        self.service = service
        self.cache = cache
        self.jupyter_port = jupyter_port
        self.delete_volume = delete_volume
        self.docker_build = docker_build
        self.os_type = platform.system().lower()
        current_dir = Path(__file__).resolve().parent
        self.project_root = current_dir

        if action == "stop":
            self.cleanup()

        if action == "restart":
            self.cleanup()
            self.start()

        if action == "start":
            self.start()

    @staticmethod
    def log(message: str):
        print(f"\033[0;34m[{datetime.now().strftime('%H:%M:%S')}]\033[0m {message}")

    @staticmethod
    def error(message: str):
        print(f"\033[0;31mERROR:\033[0m {message}", file=sys.stderr)

    def run(self, command: list, error: str):
        try:
            subprocess.call(command)
        except Exception:
            self.log(error)
            raise

    def handle_error(self, message: str):
        self.error(f"Error: {message}")
        sys.exit(1)

    def create_directory(self, dir_name):
        if not os.path.exists(dir_name):
            try:
                os.makedirs(dir_name, exist_ok=True)
                self.log(f"Created directory: {dir_name}")
            except Exception as e:
                self.handle_error(f"Failed to create {dir_name} directory: {e}")
        else:
            self.log(f"Directory {dir_name} already exists")

        try:
            os.chmod(dir_name, 0o777)
            self.log(f"Set permissions for {dir_name}")
        except Exception:
            self.log(f"Warning: Could not set permissions for {dir_name}")

    def check_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(("127.0.0.1", self.jupyter_port)) == 0:
                self.handle_error(f"Port {self.jupyter_port} is already in use.")

    def stop_jupyter(self):
        self.log(f"Attempting to stop Jupyter processes on port {self.jupyter_port}")
        for proc in psutil.process_iter(attrs=["pid", "name", "cmdline"]):
            try:
                cmdline = proc.info.get("cmdline") or []
                name = proc.info.get("name") or ""
                if any("jupyter-lab" in arg for arg in cmdline) or "jupyter" in name:
                    self.log(f"Terminating process {proc.pid} ({name})")
                    proc.terminate()
                    proc.wait(timeout=5)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

    @staticmethod
    def docker_services_for(component):
        services = {
            "airflow": ["airflow-apiserver", "airflow-scheduler",
                        "airflow-init", "airflow-dag-processor",
                        "postgres-airflow"],
            "mlflow": ["mlflow", "postgres-mlflow"],
            "minio": ["minio", "minio_client"]
        }
        return services.get(component, [])

    def docker_compose_action(self, actions, service=None):
        base_cmd = ["docker", "compose", "-f",
                    "docker/docker-compose/docker-compose.yml"]
        if service:
            services = MlopsManager.docker_services_for(service)
            print("Services:::", services, service)
            if not services:
                self.handle_error(f"Unknown service: {service}")
            cmd = base_cmd + actions + services
        else:
            cmd = base_cmd + actions

        self.log(f"Running: {' '.join(cmd)}")
        self.run(cmd, f"Error running docker compose {actions}")

    def cleanup(self):
        self.log("Shutting down Gaiaflow services...")
        if self.service == "jupyter":
            self.stop_jupyter()
        elif self.service is None:
            down_cmd = ["down"]
            if self.delete_volume:
                self.log("Removing volumes with shutdown")
                down_cmd.append("-v")
            self.docker_compose_action(down_cmd, self.service)
            self.stop_jupyter()
        else:
            down_cmd = ["down"]
            if self.delete_volume:
                self.log("Removing volumes with shutdown")
                down_cmd.append("-v")
            self.docker_compose_action(down_cmd, self.service)

        self.log("Cleanup complete")

    def start_jupyter(self):
        self.log("Starting Jupyter Lab...")
        cmd = ["jupyter", "lab", "--ip=0.0.0.0", f"--port={self.jupyter_port}"]
        subprocess.Popen(cmd)

    def update_env_file_with_airflow_uid(self, env_path=".env"):
        if self.os_type == "linux":
            uid = str(os.getuid())
        else:
            uid = 50000

        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                lines = f.readlines()

        key_found = False
        new_lines = []
        for line in lines:
            if line.strip().startswith("AIRFLOW_UID="):
                new_lines.append(f"AIRFLOW_UID={uid}\n")
                key_found = True
            else:
                new_lines.append(line)

        if not key_found:
            new_lines.append(f"AIRFLOW_UID={uid}\n")

        with open(env_path, "w") as f:
            f.writelines(new_lines)

        print(f"Set AIRFLOW_UID={uid} in {env_path}")

    def start(self):
        self.log("Setting up directories...")
        self.create_directory("../logs")
        self.create_directory("../data")
        self.update_env_file_with_airflow_uid()

        if self.service == "jupyter" or self.service is None:
            self.check_port()

        if self.docker_build:
            build_cmd = ["build"]
            if not self.cache:
                build_cmd.append("--no-cache")

            self.log("Building Docker images")
            self.docker_compose_action(build_cmd, self.service)

        if self.service is None:
            # self.start_jupyter()
            self.docker_compose_action(["up", "-d"], service=None)
        elif self.service == "jupyter":
            self.start_jupyter()
        else:
            self.docker_compose_action(["up", "-d"], service=self.service)

app = typer.Typer(help="Gaiaflow: MLOps Environment Launcher")

class Action(str, Enum):
    start = "start"
    stop = "stop"
    restart = "restart"

class Service(str, Enum):
    airflow = "airflow"
    mlflow = "mlflow"
    minio = "minio"
    jupyter = "jupyter"

@app.command()
def manage(
    action: Action = typer.Argument(..., help="Action to perform", show_choices=True),
    service: List[Service] = typer.Option(None, "--service", "-s", help="Services to manage. Use multiple --service flags, or leave empty to run all."),
    cache: bool = typer.Option(False, "--cache", "-c", help="Use Docker cache"),
    jupyter_port: int = typer.Option(8895, "--jupyter-port", "-j", help="Port for JupyterLab"),
    delete_volume: bool = typer.Option(False, "--delete-volume", "-v", help="Delete volumes on shutdown"),
    docker_build: bool = typer.Option(False, "--docker-build", "-b", help="Force Docker image build"),
):
    """
    Start, stop, or restart selected MLOps services.
    """
    allowed_actions = {"start", "stop", "restart"}
    if action not in allowed_actions:
        typer.echo(f"Invalid action '{action}'. Must be one of: {', '.join(allowed_actions)}")
        raise typer.Exit(1)
    typer.echo(f"Selected services: {service}")
    print("cwd::", os.getcwd())
    if service:
        for s in service:
            typer.echo(f"Running {action} on {s}...")
            MlopsManager(
                action=action,
                service=s,
                cache=cache,
                jupyter_port=jupyter_port,
                delete_volume=delete_volume,
                docker_build=docker_build,
            )
    else:
        typer.echo(f"Running {action} with all services")
        MlopsManager(
            action=action,
            service=None,
            cache=cache,
            jupyter_port=jupyter_port,
            delete_volume=delete_volume,
            docker_build=docker_build,
        )

def main():
    app()

if __name__ == "__main__":
    app()