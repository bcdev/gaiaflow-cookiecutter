import argparse
import os
import subprocess
import sys
import shutil
from datetime import datetime
from typing import Any

from docker_config import DOCKER_IMAGE_NAME

class MinikubeManager:
    def __init__(self, clean=False, stop=False):
        self.minikube_profile = "airflow"
        self.docker_image_name = DOCKER_IMAGE_NAME
        self.clean = clean
        if stop:
            self.stop_minikube()

    @staticmethod
    def log(message):
        print(f"\033[0;34m[{datetime.now().strftime('%H:%M:%S')}]\033[0m {message}")

    @staticmethod
    def error(message):
        print(f"\033[0;31mERROR:\033[0m {message}", file=sys.stderr)
        sys.exit(1)

    def run(self, command: list, error: str, env=None):
        try:
            return subprocess.check_call(command, env=env)
        except subprocess.CalledProcessError:
            self.log(error)

    def cleanup(self):
        self.log("Performing cleanup...")

        if shutil.which("minikube"):
            result = subprocess.run(
                f"minikube profile list | grep '^{self.minikube_profile} '",
                shell=True,
                stdout=subprocess.DEVNULL,
            )
            if result.returncode == 0:
                self.log(f"Stopping and deleting profile: {self.minikube_profile}")
                self.run(
                    ["minikube", "stop", "--profile", self.minikube_profile],
                    f"Error stopping minikube cluster profile [{
                        self.minikube_profile
                    }]",
                )
                self.run(
                    ["minikube", "delete", "--profile", self.minikube_profile],
                    "Error deleting minikube cluster "
                    f"profile [{self.minikube_profile}]",
                )

            if self.clean:
                self.log("Full cleanup: removing all minikube data")
                self.run(["minikube", "delete", "--all", "--purge"], "Error "
                                                                     "deleting minikube")
                shutil.rmtree(os.path.expanduser("~/.minikube"), ignore_errors=True)
                shutil.rmtree(os.path.expanduser("~/.kube"), ignore_errors=True)
                minikube_path = shutil.which("minikube")
                if minikube_path:
                    self.run(
                        ["sudo", "rm", "-f", minikube_path],
                        f"Error removing {minikube_path}",
                    )
        else:
            self.error(
                "Minikube not found. Please follow the documentation to install it."
            )

    # def install_minikube(self):
    #     self.log("Installing minikube...")
    #     os_type = platform.system().lower()
    #     arch = platform.machine()
    #     arch = {"x86_64": "amd64", "aarch64": "arm64"}.get(arch, None)
    #     if not arch:
    #         self.error("Unsupported architecture.")
    #         sys.exit(1)
    #
    #     url = f"https://github.com/kubernetes/minikube/releases/latest/download/minikube-{os_type}-{arch}"
    #     subprocess.check_call(["curl", "-LO", url])
    #     subprocess.check_call(["sudo", "install", f"minikube-{os_type}-{arch}", "/usr/local/bin/minikube"])
    #     os.remove(f"minikube-{os_type}-{arch}")
    #     self.log("Minikube installed")

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
                self.log(
                    f"Minikube cluster [{self.minikube_profile}] is already running."
                )
                self.log("Switching Docker context to Minikube...")
                os.system(f"eval $(minikube -p {self.minikube_profile} docker-env)")
                return
        except subprocess.CalledProcessError:
            self.log(f"Minikube cluster [{self.minikube_profile}] is not running.")

        self.log(f"Starting Minikube cluster [{self.minikube_profile}]...")
        self.run(
            [
                "minikube",
                "start",
                "--profile",
                self.minikube_profile,
                "--driver=docker",
                "--cpus=4",
                "--memory=4g",
            ], f"Error starting minikube profile [{self.minikube_profile}]"
        )

        self.log("Switching Docker context to Minikube...")
        os.system(f"eval $(minikube -p {self.minikube_profile} docker-env)")



    def stop_minikube(self):
        self.log(f"Stopping minikube profile [{self.minikube_profile}]...")
        try:
            self.run(
                [
                    "minikube",
                    "stop",
                    "--profile",
                    self.minikube_profile,
                ], f"Error stopping minikube profile [{self.minikube_profile}]"
            )
        except subprocess.CalledProcessError as e:
            raise
        self.log(f"Stopping minikube profile [{self.minikube_profile}] "
                 "successful.")

    def build_docker_image(self):
        if not os.path.exists("Dockerfile"):
            self.error("Dockerfile not found")
            sys.exit(1)
        self.log(f"Building Docker image [{self.docker_image_name}]...")
        env = os.environ.copy()
        result = subprocess.run(
            ["minikube", "-p", self.minikube_profile, "docker-env"],
            stdout=subprocess.PIPE,
            check=True,
        )
        for line in result.stdout.decode().splitlines():
            if line.startswith("export "):
                key, value = line.replace("export ", "").split("=", 1)
                env[key] = value.strip('"')
        self.run(["docker", "build", "-t", self.docker_image_name, "."],
                 "Error building docker image.", env=env)

    def create_kube_config_inline(self):
        filename = "kube_config_inline"
        self.log("Creating kube config inline file...")
        with open(filename, "w") as f:
            subprocess.check_call(
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
        if os.path.exists(filename):
            self.log(f"Created kube config inline file {filename}")

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
            "my-minio-creds",
        ]
        result = subprocess.run(
            check_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        if result.returncode == 0:
            self.log(f"Secret [{secret_name}] already exists. Skipping creation.")
        else:
            self.log(f"Creating secret [{secret_name}]...")
            subprocess.check_call(
                [
                    "minikube",
                    "kubectl",
                    "-p",
                    self.minikube_profile,
                    "--",
                    "create",
                    "secret",
                    "generic",
                    "my-minio-creds",
                    "--from-literal=AWS_ACCESS_KEY_ID=minio",
                    "--from-literal=AWS_SECRET_ACCESS_KEY=minio123",
                ]
            )

    def start(self):
        self.log("Starting Local KPO test setup...")
        # self.cleanup()
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

        self.log(
            f"Minikube cluster [{self.minikube_profile}] is up and running. Have fun!"
        )


def main():
    parser = argparse.ArgumentParser(description="Minikube manager")
    parser.add_argument(
        "-c", "--clean", action="store_true", help="Remove minikube from system."
    )
    parser.add_argument(
        "-s", "--stop", action="store_true", help="Stop minikube cluster"
    )
    args = parser.parse_args()
    minikube = MinikubeManager(clean=args.clean, stop=args.stop)
    if not args.stop:
        minikube.start()


if __name__ == "__main__":
    main()
