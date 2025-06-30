import argparse
import os
import signal
import socket
import subprocess
import sys
from datetime import datetime
import psutil
import platform


class MlopsManager:
    def __init__(self, action=None, service=None, cache=False, jupyter_port=8895, delete_volume=False, docker_build=False):
        self.action = action
        self.service = service
        self.cache = cache
        self.jupyter_port = jupyter_port
        self.delete_volume = delete_volume
        self.docker_build = docker_build

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
            return subprocess.check_call(command)
        except subprocess.CalledProcessError:
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
            "airflow": ["airflow-webserver", "airflow-scheduler", "airflow-init", "postgres-airflow"],
            "mlflow": ["mlflow", "postgres-mlflow", "minio", "minio_client"],
        }
        return services.get(component, [])

    def docker_compose_action(self, actions, service=None):
        base_cmd = ["docker", "compose"]
        if service:
            services = MlopsManager.docker_services_for(service)
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

    def start(self):
        self.log("Setting up directories...")
        self.create_directory("logs")
        self.create_directory("data")

        if self.service == "jupyter":
            self.check_port()

        if self.docker_build:
            build_cmd = ["docker", "compose", "build"]
            if not self.cache:
                build_cmd.append("--no-cache")
            self.log("Building Docker images")
            self.run(build_cmd, "Error during Docker build")

        if self.service == "jupyter":
            self.start_jupyter()
        else:
            self.docker_compose_action(["up", "-d"], service=self.service)


def main():
    parser = argparse.ArgumentParser(description="Gaiaflow: MLOps Environment Launcher")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--start", action="store_true", help="Start services")
    group.add_argument("--stop", action="store_true", help="Stop services")
    group.add_argument("--restart", action="store_true", help="Restart services")

    parser.add_argument(
        "--service", choices=["airflow", "mlflow", "jupyter"], help="Service to start/stop/restart"
    )
    parser.add_argument("-c", "--cache", action="store_true", help="Enable Docker cache")
    parser.add_argument("-j", "--jupyter-port", type=int, default=8895, help="Jupyter port")
    parser.add_argument("-v", "--delete-volume", action="store_true", help="Delete volumes on shutdown")
    parser.add_argument("-b", "--docker-build", action="store_true", help="Force Docker build")

    args = parser.parse_args()

    action = "start" if args.start else "stop" if args.stop else "restart"

    MlopsManager(
        action=action,
        service=args.service,
        cache=args.cache,
        jupyter_port=args.jupyter_port,
        delete_volume=args.delete_volume,
        docker_build=args.docker_build,
    )


if __name__ == "__main__":
    main()
