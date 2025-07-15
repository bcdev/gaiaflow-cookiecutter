import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
import typer

import yaml

from .gen_docker_image_name import DOCKER_IMAGE_NAME


class MinikubeManager:
    def __init__(self, stop=False, start=False, restart=False, build_only=False, create_config_only=False):
        self.minikube_profile = "airflow"
        self.docker_image_name = DOCKER_IMAGE_NAME
        self.build_only = build_only
        self.os_type = platform.system().lower()

        if stop:
            self.stop_minikube()
        elif restart:
            self.stop_minikube()
            self.start_minikube()
        elif start:
            self.start_minikube()
        elif build_only:
            self.build_docker_image()
        elif create_config_only:
            self.create_kube_config_inline()

    @staticmethod
    def log(message):
        print(f"\033[0;34m[{datetime.now().strftime('%H:%M:%S')}]\033[0m {message}")

    @staticmethod
    def error(message):
        print(f"\033[0;31mERROR:\033[0m {message}", file=sys.stderr)
        sys.exit(1)

    def run(self, command: list, error: str, env=None):
        if env is None:
            env = os.environ
        try:
            subprocess.run(command, env=env, check=True)
        except subprocess.CalledProcessError:
            self.error(error)

    def start_minikube(self):
        self.log(f"Checking Minikube cluster [{self.minikube_profile}] status...")
        try:
            result = subprocess.run(
                ["minikube", "status", "--profile", self.minikube_profile],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            if b"Running" in result.stdout:
                self.log(f"Minikube cluster [{self.minikube_profile}] is already running.")
        except subprocess.CalledProcessError:
            self.log(f"Minikube cluster [{self.minikube_profile}] is not running. Starting...")

            self.run(
                [
                    "minikube",
                    "start",
                    "--profile",
                    self.minikube_profile,
                    "--driver=docker",
                    "--cpus=4",
                    "--memory=4g",
                ],
                f"Error starting minikube profile [{self.minikube_profile}]"
            )

        self.create_kube_config_inline()
        self.restart_docker_compose()

    def stop_minikube(self):
        self.log(f"Stopping minikube profile [{self.minikube_profile}]...")
        self.run(["minikube", "stop", "--profile", self.minikube_profile],
                 f"Error stopping minikube profile [{self.minikube_profile}]")
        self.run(["minikube", "delete", "--profile", self.minikube_profile],
                 f"Error deleting minikube profile [{self.minikube_profile}]")
        self.log(f"Stopped minikube profile [{self.minikube_profile}]")

    def build_docker_image(self):
        if not Path("Dockerfile").exists():
            self.error("Dockerfile not found")
        self.log(f"Building Docker image [{self.docker_image_name}]...")

        result = subprocess.run(
            ["minikube", "-p", self.minikube_profile, "docker-env", "--shell", "bash"],
            stdout=subprocess.PIPE,
            check=True,
        )
        env = os.environ.copy()
        for line in result.stdout.decode().splitlines():
            if line.startswith("export "):
                try:
                    key, value = line.replace("export ", "").split("=", 1)
                    env[key.strip()] = value.strip('"')
                except ValueError:
                    continue
        self.run(["docker", "build", "-t", self.docker_image_name, "."],
                 "Error building docker image.", env=env)

    def create_kube_config_inline(self):
        kube_config = Path.home() / ".kube" / "config"
        backup_config = kube_config.with_suffix(".backup")
        print("pwd", os.getcwd())
        filename = "../kube_config_inline"

        if self.os_type == "windows" and kube_config.exists():
            self.log("Detected Windows: patching kube config with host.docker.internal")
            with open(kube_config, "r") as f:
                config_data = yaml.safe_load(f)

            with open(backup_config, "w") as f:
                yaml.dump(config_data, f)

            for cluster in config_data.get("clusters", []):
                server = cluster.get("cluster", {}).get("server", "")
                if "127.0.0.1" in server or "localhost" in server:
                    cluster["cluster"]["server"] = server.replace("127.0.0.1", "host.docker.internal").replace("localhost", "host.docker.internal")

            with open(kube_config, "w") as f:
                yaml.dump(config_data, f)

        self.log("Creating kube config inline file...")
        with open(filename, "w") as f:
            subprocess.call(
                [
                    "minikube",
                    "kubectl",
                    "--",
                    "config",
                    "view",
                    "--flatten",
                    "--minify",
                    "--raw",
                ],
                stdout=f,
            )

        self.log(f"Created kube config inline file {filename}")

        self.log(f"Adding insecure-skip-tls-verfiy for local setup in kube config inline file {filename}")

        with open(filename, "r") as f:
            kube_config_data = yaml.safe_load(f)

        if self.os_type == "windows":
            for cluster in kube_config_data.get("clusters", []):
                cluster_data = cluster.get("cluster", {})
                if "insecure-skip-tls-verify" not in cluster_data:
                    cluster_data["insecure-skip-tls-verify"] = True

        self.log(f"Saving kube config inline file {filename}")
        with open(filename, "w") as f:
            yaml.safe_dump(kube_config_data, f, default_flow_style=False)

        if self.os_type == "windows" and backup_config.exists():
            shutil.copy(backup_config, kube_config)
            backup_config.unlink()
            self.log("Reverted kube config to original state.")

    def create_secrets(self, secret_name: str, secret_data: dict[str, Any]):
        self.log(f"Checking if secret [{secret_name}] exists...")
        check_cmd = [
            "minikube",
            "kubectl",
            "-p",
            self.minikube_profile,
            "--",
            "get",
            "secret",
            secret_name,
        ]
        result = subprocess.run(
            check_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        if result.returncode == 0:
            self.log(f"Secret [{secret_name}] already exists. Skipping creation.")
        else:
            self.log(f"Creating secret [{secret_name}]...")
            create_cmd = [
                "minikube",
                "kubectl",
                "-p",
                self.minikube_profile,
                "--",
                "create",
                "secret",
                "generic",
                secret_name,
            ]
            for k, v in secret_data.items():
                create_cmd.append(f"--from-literal={k}={v}")
            subprocess.check_call(create_cmd)

    def start(self):
        self.log("Starting full setup...")
        self.start_minikube()
        self.build_docker_image()
        self.create_kube_config_inline()
        self.create_secrets(
            secret_name="my-minio-creds",
            secret_data={
                "AWS_ACCESS_KEY_ID": "minio",
                "AWS_SECRET_ACCESS_KEY": "minio123",
            },
        )
        self.log(f"Minikube cluster [{self.minikube_profile}] is ready!")

    def restart_docker_compose(self):
        self.log("Restarting Docker Compose services...")
        self.run(["docker", "compose", "-f",
                  "docker/docker-compose/docker-compose.yml", "down"],
                 "Error running docker compose down")
        self.run(["docker", "compose", "-f",
                        "docker/docker-compose/docker-compose.yml", "-f",
                        "docker/docker-compose/docker-compose-minikube-network.yml",
                        "up", "-d"], "Error running docker compose up")

app = typer.Typer()

@app.command()
def manage(
    stop: bool = typer.Option(False, "--stop", "-s", help="Stop minikube cluster"),
    restart: bool = typer.Option(False, "--restart", "-r", help="Restart minikube cluster"),
    start: bool = typer.Option(False, "--start", help="Start minikube cluster"),
    build_only: bool = typer.Option(False, "--build-only", help="Only build docker image inside minikube"),
    create_config_only: bool = typer.Option(False, "--create-config-only", help="Create inline config for Docker compose."),
    create_secrets: bool = typer.Option(False, "--create-secrets", help="Create secrets for pods (Deprecated)"),
):
    print("pwd", os.getcwd())
    manager = MinikubeManager()

    if stop:
        manager.stop_minikube()
    elif restart:
        manager.stop_minikube()
        manager.start_minikube()
    elif start:
        manager.start_minikube()
    elif build_only:
        manager.build_docker_image()
    elif create_config_only:
        manager.create_kube_config_inline()

    if create_secrets:
        manager.create_secrets(
            secret_name="my-minio-creds",
            secret_data={
                "AWS_ACCESS_KEY_ID": "minio",
                "AWS_SECRET_ACCESS_KEY": "minio123",
            },
        )

def main():
    app()

if __name__ == "__main__":
    app()
