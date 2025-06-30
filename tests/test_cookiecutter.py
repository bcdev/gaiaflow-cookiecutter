import pathlib
import shutil
import subprocess
import tempfile
from itertools import product
from typing import Any

import yaml
import pytest
from cookiecutter.main import cookiecutter

BASE_CONTEXT = {
    "project_name": "My ml project",
    "project_description": "Some description",
    "author_name": "John Doe",
    "author_email": "john@doe.com",
    "folder_name": "my_ml_project",
    "package_name": "my_package",
}

CORE_FILES = {
    "mlops_manager.py",
    "minikube_manager.py",
    "kube_config_inline",
    "utils.py",
    "docker_config.py",
    "docker-compose.yml",
    "README.md",
    ".env",
    ".gitignore",
    "MLOPS.md",
    "environment.yml",
    "dags/README.md",
    "dockerfiles/README.md",
    "dockerfiles/mlflow/requirements.txt",
    "dockerfiles/mlflow/Dockerfile",
    "dockerfiles/airflow/Dockerfile",
    "notebooks/README.md",
    "notebooks/examples/mlflow_direct_inference.ipynb",
    "notebooks/examples/mlflow_local_deploy_inference.ipynb",
    "notebooks/examples/mlfow_introduction.ipynb",
    "data/add_your_data_here",
    "my_package/README.md",
    "my_package/__init__.py",
    "my_package/dataloader/change_me_data.py",
    "my_package/dataloader/__init__.py",
    "my_package/utils/utils.py",
    "my_package/utils/__init__.py",
    "my_package/model_pipeline/change_me_model_pipeline.py",
    "my_package/model_pipeline/__init__.py",
    "my_package/models/change_me_model.py",
    "my_package/models/__init__.py",
    "my_package/train/change_me_train.py",
    "my_package/train/__init__.py",
    "my_package/postprocess/change_me_postprocess.py",
    "my_package/postprocess/__init__.py",
    "my_package/preprocess/change_me_preprocess.py",
    "my_package/preprocess/__init__.py",
}

MANUAL_DAGS_FILES = [
    "dags/change_me_task_factory_dag.py",
]

EXAMPLE_MANUAL_DAGS_FILES = [
    "dags/example_task_factory_dag.py",
]

EXAMPLE_ML_PACKAGE_FILES = [
    "my_package/dataloader/example_data.py",
    "my_package/model_pipeline/example_model_pipeline.py",
    "my_package/postprocess/example_postprocess.py",
    "my_package/preprocess/example_preprocess.py",
    "my_package/train/example_train.py",
    "my_package/models/example_model.py",
]


# Possible choices for each parameter to create combinations of them.
PARAMETER_OPTIONS = {
    "show_examples": ["yes", "no"],
}


def generate_test_cases():
    param_names = list(PARAMETER_OPTIONS.keys())
    param_values = list(PARAMETER_OPTIONS.values())

    test_cases = []

    for values in product(*param_values):
        context = BASE_CONTEXT.copy()
        context.update(dict(zip(param_names, values)))

        expects = {
            "examples": context["show_examples"] == "yes",
        }

        test_cases.append({"context": context, "expects": expects})

    return test_cases


TEST_CASES = generate_test_cases()


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)


def generate_project(temp_dir: str, context: dict[str, Any]) -> pathlib.Path:
    template_dir = str(pathlib.Path(__file__).parent.parent)
    cookiecutter(
        template=template_dir,
        no_input=True,
        extra_context=context,
        output_dir=temp_dir,
    )
    return pathlib.Path(temp_dir) / context["folder_name"]


def get_all_files(directory: pathlib.Path) -> set[str]:
    return {
        str(path.relative_to(directory))
        for path in directory.glob("**/*")
        if path.is_file()
    }


@pytest.mark.parametrize("test_case", TEST_CASES)
def test_project_generation(temp_dir: str, test_case: dict[str, Any]):
    context = test_case["context"]
    expects = test_case["expects"]
    project_dir = generate_project(temp_dir, context)

    assert project_dir.exists(), "Project directory not created"

    readme_content = (project_dir / "README.md").read_text(encoding="utf-8")
    assert context["project_name"] in readme_content, "Project name not in " "README"

    env_path = project_dir / "environment.yml"
    with env_path.open(encoding="utf-8") as f:
        env_data = yaml.safe_load(f)
        assert context["folder_name"] in env_data["name"], "Wrong environment name"

    docker_compose = (project_dir / "docker-compose.yml").read_text()
    minio_configs = [
        "MINIO_ROOT_USER",
        "MINIO_ROOT_PASSWORD",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "MLFLOW_S3_ENDPOINT_URL",
    ]
    artifact_config = "--default-artifact-root s3://${MLFLOW_BUCKET_NAME} --artifacts-destination s3://${MLFLOW_BUCKET_NAME}"

    for config in minio_configs:
        assert config in docker_compose
    assert artifact_config in docker_compose

    actual_files = get_all_files(project_dir)
    core_files_copy = CORE_FILES.copy()

    if expects["examples"]:
        core_files_copy.update(EXAMPLE_MANUAL_DAGS_FILES)
        core_files_copy.update(EXAMPLE_ML_PACKAGE_FILES)

    core_files_copy.update(MANUAL_DAGS_FILES)

    for file in core_files_copy:
        assert file in actual_files, f"Missing core file: {file}"

    for file in MANUAL_DAGS_FILES:
        assert file in actual_files, f"Missing manual DAG file: {file}"

    if expects["examples"]:
        for file in EXAMPLE_MANUAL_DAGS_FILES:
            assert file in actual_files, f"Unexpected manual example DAG file: {file}"
        for file in EXAMPLE_ML_PACKAGE_FILES:
            assert file in actual_files, f"Missing ML pacakge example file{file}"


@pytest.mark.parametrize("test_case", TEST_CASES)
def test_ruff_linting(temp_dir: str, test_case: dict[str, Any]):
    project_dir = generate_project(temp_dir, test_case["context"])
    result = subprocess.run(
        ["ruff", "check", "."],
        cwd=str(project_dir),
        capture_output=True,
        text=True,
    )
    assert (
        result.returncode == 0
    ), f"Linting failed:\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
