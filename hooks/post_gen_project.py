import os
import subprocess
from pathlib import Path
import shutil
import sys

import ruamel.yaml
from ruamel.yaml import CommentedMap


def remove_file(file_path):
    """Remove a file if it exists."""
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"Removed file: {file_path}")
        except Exception as e:
            print(f"Error removing file {file_path}: {e}")
    else:
        print(f"File not found on path: {file_path}")


def remove_directory(dir_path):
    """Remove a directory and all its contents if it exists."""
    if os.path.exists(dir_path):
        try:
            shutil.rmtree(dir_path)
            print(f"Removed directory: {dir_path}")
        except Exception as e:
            print(f"Error removing directory {dir_path}: {e}")


def modify_environment_yaml(env_file: Path, to_be_deleted_deps: list[str]):
    """Remove unwanted libraries from environment.yml based on user input."""
    if not Path.exists(env_file):
        print(f"{str(env_file)} not found.")
        return

    yaml = ruamel.yaml.YAML()
    yaml.indent(offset=2)

    try:
        env_data = yaml.load(env_file)
    except Exception as e:
        print(f"Error reading {str(env_file)}: {e}")
        return

    dependencies = env_data.get("dependencies", [])

    for i in range(len(dependencies) - 1, -1, -1):
        dep = dependencies[i]
        if (
            isinstance(dep, CommentedMap) and dict(dep) in to_be_deleted_deps
        ) or dep in to_be_deleted_deps:
            dependencies.remove(dep)

    try:
        with open(env_file, "w") as f:
            yaml.dump(env_data, f)
        print(f"Updated {env_file}")
    except Exception as e:
        print(f"Error writing {env_file}: {e}")


def update_environment_files():
    file_paths_config = [
        "pyproject.toml",
        "environment.yml",
    ]

    for path in file_paths_config:
        full_file_path = os.path.join(os.getcwd(), path)
        remove_file(full_file_path)

    move_package_into_src()

    pixi_pyproject = "pixi_pyproject.toml"
    full_pixi_pyproject_path = Path(os.getcwd(), pixi_pyproject)
    full_pyproject_path = Path(os.getcwd(), "pyproject.toml")
    full_pixi_pyproject_path.rename(full_pyproject_path)


def move_package_into_src():
    package_name = "{{ cookiecutter.package_name }}"

    root_pkg = Path(package_name)
    src_pkg = Path("src") / package_name

    shutil.rmtree(src_pkg, ignore_errors=True)

    print(f"Moving {root_pkg} to {src_pkg}")
    shutil.move(str(root_pkg), str(src_pkg))


def run(cmd, check=True):
    print(f"> {' '.join(cmd)}")
    subprocess.run(cmd, check=check)


def main():
    show_examples = "{{ cookiecutter.show_examples }}".strip().lower()
    environment_manager = "{{ cookiecutter.environment_manager }}"

    if show_examples != "yes":
        file_paths_config = [
            "dataloader/example_data.py",
            "model_pipeline/example_model_pipeline.py",
            "models/example_model.py",
            "postprocess/example_postprocess.py",
            "preprocess/example_preprocess.py",
            "train/example_train.py",
            "dags/example_config.yml",
            "dags/example_dag.py",
        ]

        for file_path_relative in file_paths_config:
            full_file_path = os.path.join(
                os.getcwd(), "{{ cookiecutter.package_name }}", file_path_relative
            )
            remove_file(full_file_path)

    if environment_manager == "pixi":
        update_environment_files()


if __name__ == "__main__":
    sys.exit(main())
