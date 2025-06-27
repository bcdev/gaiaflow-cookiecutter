import os

with open(os.path.join(os.path.dirname(__file__), "frijun", "version.py")) as f:
    __version__ = f.read().strip().split('"')[1]

PACKAGE_NAME = "my-package"
IMAGE_REPO = "my-local-image"  # Change to your ECR repo for prod

DOCKER_IMAGE_NAME = f"{IMAGE_REPO}/{PACKAGE_NAME}:{__version__}"
print(DOCKER_IMAGE_NAME)