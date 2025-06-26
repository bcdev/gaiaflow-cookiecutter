import argparse
import os
import signal
import socket
import subprocess
import sys
from datetime import datetime


class MlopsManager:
    def __init__(
        self,
        cache=False,
        jupyter_port=8895,
        delete_volume=False,
        docker_build=False,
        stop_services=False,
    ):
        self.cache = cache
        self.jupyter_port = jupyter_port
        self.delete_volume = delete_volume
        self.docker_build = docker_build

        if stop_services:
            self.cleanup()

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

    def cleanup(self, *args):
        self.log("Shutting down Gaiaflow services...")
        down_command = ["docker", "compose", "down"]
        if self.delete_volume:
            self.log("Shutting down Docker with deleting volumes")
            down_command.append("-v")
        else:
            self.log("Shutting down Docker without deleting volumes")
        self.run(down_command, "Error shutting down docker services")

        self.run(
            ["kill", "$(lsof -t -i:{0} -sTCP:LISTEN)".format(self.jupyter_port)],
            "Warning: Jupyter shutdown failed or was not running.",
        )
        self.log("Shutting down Jupyter")

        self.log("Cleanup complete")

    def start(self):
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)

        self.log("Setting up directories...")
        self.create_directory("logs")
        self.create_directory("data")

        self.check_port()

        self.log("Starting Docker Compose services...")

        if self.docker_build:
            build_cmd = ["docker", "compose", "build"]
            if not self.cache:
                build_cmd.append("--no-cache")

            self.log("Running: " + " ".join(build_cmd))
            self.run(build_cmd, "Error running docker compose")

        up_cmd = ["docker", "compose", "up", "-d"]
        self.log("Running: " + " ".join(up_cmd))
        self.run(up_cmd, "Error running docker compose")

        self.log("Starting Jupyter Lab...")
        subprocess.Popen(
            ["jupyter", "lab", "--ip=0.0.0.0", f"--port={self.jupyter_port}"]
        )

        signal.pause()


def main():
    parser = argparse.ArgumentParser(description="Gaiaflow: Mlops environment launcher")
    parser.add_argument(
        "-c",
        "--cache",
        action="store_true",
        help="Enable Docker cache. Can only be provided if using docker build flag -b",
    )
    parser.add_argument(
        "-j", "--jupyter-port", type=int, default=8895, help="Jupyter port"
    )
    parser.add_argument(
        "-v", "--delete-volume", action="store_true", help="Delete volumes on shutdown"
    )
    parser.add_argument(
        "-b", "--docker-build", action="store_true", help="Force Docker build"
    )
    parser.add_argument(
        "-s", "--stop", action="store_true", help="Stop Gaiaflow services"
    )

    args = parser.parse_args()

    manager = MlopsManager(
        cache=args.cache,
        jupyter_port=args.jupyter_port,
        delete_volume=args.delete_volume,
        docker_build=args.docker_build,
        stop_services=args.stop,
    )
    if not args.stop:
        manager.start()


if __name__ == "__main__":
    main()
