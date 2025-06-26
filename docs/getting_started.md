# Getting Started with GaiaFlow

This guide will help you set up your environment, install dependencies, and generate your first project using the GaiaFlow template.

---

## Prerequisites

Before starting, ensure you have the following installed:

- **Docker** and **Docker Compose plugin** (tested with Docker 27.x and Compose v2.x)
- **Mamba** (or Conda) package manager, preferably with Python 3.12
- A Github account with membership in the `bcdev` organization (for production deployment)

---

### Installing Docker and Docker Compose Plugin

Follow the official Docker guide to install on Ubuntu:

- [Docker Installation](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)
- This installs both the Docker engine and the Docker Compose plugin.

Verify installation by running:

```bash
docker --version
docker compose version
```
You should see output similar to:

```commandline
Docker version 27.5.1, build 9f9e405
Docker Compose version v2.32.4
```

### Installing Mamba and Setting Up Python Environment

Mamba is a faster alternative to Conda for managing environments.
1. Install Miniforge (recommended)
2. Create and activate a new environment for Cookiecutter:
```bash
mamba create -n cc python=3.12 cookiecutter ruamel.yaml -y
mamba activate cc
```

### Generating a New Project from GaiaFlow Template
Run the following to scaffold your project structure:

```bash
cookiecutter https://github.com/bcdev/gaiaflow
```

You will be prompted for several inputs such as:
- Project name
- Package name
- Author details
- Description etc.

If you skip an input, the default option will be used.

### Starting Your Local MLOps Environment

After project creation, navigate into your new project folder.

Run the MLOps services locally using the provided `GaiaflowManager`.
You can read more about the usage [here](gaiaflow_manager.md)



