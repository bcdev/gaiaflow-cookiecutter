# Gaiaflow Manager

## 1. What This Script Does

`gaiaflow_manager.py` is an internal MLOps framework designed for data scientists and engineers. 
It enables a local development environment using Docker Compose for rapid experimentation, testing, 
and iteration of machine learning pipelines, including services like Jupyter and Airflow.

## 2. How to Use It

```bash
python gaiaflow_manager.py [OPTIONS]
```

Example:

```bash
python gaiaflow_manager.py -b --no-cache
```

To stop services:

```bash
python gaiaflow_manager.py -s
```

## 3. What Different Options Mean

| Option | Description |
|--------|-------------|
| `-c`, `--cache` | Use Docker build cache. Effective only with `-b` |
| `-j`, `--jupyter-port` | Port for Jupyter Lab (default: 8895) |
| `-v`, `--delete-volume` | Delete Docker volumes on shutdown |
| `-b`, `--docker-build` | Force a Docker image rebuild |
| `-s`, `--stop` | Stop running services and perform cleanup |

## 4. When to Use It

Use Gaiaflow Manager in **development mode** when:

- You're iterating on pipeline code.
- You want to test Airflow DAGs, Jupyter notebooks, or other services locally.
- You need fast feedback loops before deploying to Minikube or production.

## 5. Prerequisites

Ensure the following are installed:

- [Docker](https://docs.docker.com/get-docker/)
- [Python 3.8+](https://www.python.org/downloads/)
- [Conda or Mamba](https://docs.conda.io/en/latest/miniconda.html)

## 6. Typical Dev Workflow

1. Start the environment:

    ```bash
    python gaiaflow_manager.py -b
    ```


Accessing the services

Wait for the services to start (usually take 2-3 mins, might take longer if you 
start it without cache)

- Airflow UI: http://localhost:8080
  - Login Details:
    - username: `admin`
    - password: `admin`
- MLflow UI: http://localhost:5000
- JupyterLab: Opens up JupyterLab automatically at port 8895
- Minio (Local S3): http://localhost:9000
  - Login Details:
    - username: `minio`
    - password: `minio123`
2. Work with Jupyter on `http://localhost:8895`
3. Update code, rebuild if necessary:

    ```bash
    python gaiaflow_manager.py -b --no-cache
    ```

4. Stop services when done:

    ```bash
    python gaiaflow_manager.py -s
    ```

## 7. Troubleshooting Tips

- If you get `Port already in use`, change it with `-j` or free the port.
- Use `-v` to clean up Docker volumes if service states become inconsistent.
- Logs are saved in the `logs/` directory.

## 8. Notes

- This is **for development only**, not for production.
- Ensure Docker images used here match the ones in your production (e.g. on AWS EKS).
