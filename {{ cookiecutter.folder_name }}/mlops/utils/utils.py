import re
import subprocess


def docker_network_gateway(network_name: str = "airflow") -> str | None:
    try:
        result = subprocess.run(
            ["docker", "network", "inspect", network_name],
            check=True,
            capture_output=True,
            text=True,
        )

        for line in result.stdout.splitlines():
            if "Gateway" in line:
                match = re.search(r'"Gateway"\s*:\s*"([^"]+)"', line)
                if match:
                    return match.group(1)
        return None

    except subprocess.CalledProcessError as e:
        print(f"Error running docker network inspect: {e}")
        return None
    except FileNotFoundError:
        print("Docker command not found. Is Docker installed and in your PATH?")
        return None