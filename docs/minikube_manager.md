# Minikube Manager

## 1. What This Script Does

`minikube_manager.py` creates a local Kubernetes cluster using Minikube to 
simulate a production-like environment for ML pipelines. It allows testing 
Docker images and services under a K8s setup similar to AWS EKS.

## 2. How to Use It

```bash
python minikube_manager.py [OPTIONS]
```

Example:

```bash
python minikube_manager.py
```

To stop the cluster:

```bash
python minikube_manager.py -s
```

To remove Minikube completely:

```bash
python minikube_manager.py -c
```

## 3. What Different Options Mean

| Option | Description |
|--------|-------------|
| `-c`, `--clean` | Fully remove all Minikube data and binaries |
| `-s`, `--stop` | Stop the Minikube cluster only |

## 4. When to Use It

Use Minikube Manager when:

- You want to test Docker images and airflow tasks in a local Kubernetes environment.
- You’re preparing for deployment to production on AWS EKS.

## 5. Prerequisites

Ensure the following are installed:

- [Docker](https://docs.docker.com/get-docker/)
- [Python 3.8+](https://www.python.org/downloads/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [Conda or Mamba](https://docs.conda.io/en/latest/miniconda.html)

## 6. Environment Parity with Production

This setup is **only for local testing**. Users are responsible for:

- Ensuring the same environment exists in production.
- Using the same Docker image for local testing and production (e.g. same tag/version).

## 7. Managing Secrets

You can now create any secrets dynamically:

```python
create_secrets(secret_name="my-creds", secret_data={"API_KEY": "1234", "ENV": "dev"})
```

This creates Kubernetes secrets inside the Minikube cluster.

**Best Practice:** Use environment variables or secure vaults in production. Avoid hardcoding secrets.

## 8. Image Naming Best Practices

We recommend using:

```text
<package-name>:<version>
```

Where `version` is fetched from your Python package's `__version__`.


## 9. OS Compatibility

Tested on Linux/macOS. For Windows:

- Use [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) with Ubuntu.
- Avoid native CMD/PowerShell (may break due to signal handling or Unix-only CLI).
Please report any issues.

## 10. Typical Workflow

```bash
python minikube_manager.py        # Set up cluster
# Dev work happens...
python minikube_manager.py -s     # Stop cluster when done
```

To completely clean:

```bash
python minikube_manager.py -c
```

## 11. Notes

- Designed for internal use only.
- Docker image versioning and environment parity are **critical** for reliable results.
