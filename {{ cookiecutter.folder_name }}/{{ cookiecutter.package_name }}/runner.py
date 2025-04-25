# !!PLEASE DO NOT EDIT/DELETE THIS!!
# This file is the main entry point to your package when using Airflow to
# create DAGs from the task_factory.
# It imports the required function from your package and executes it with the
# arguments provided

import importlib
import json
import os

def run(func_path=None, kwargs=None):
    if not func_path:
        func_path = os.environ.get("FUNC_PATH", "")
        kwargs = json.loads(os.environ.get("FUNC_KWARGS", "{}"))
    if func_path:
        module_path, func_name = func_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        func = getattr(module, func_name)

        print(f"Running {func_path} with args: {kwargs}")
        result = func(**kwargs)
        print("Function result:", result)
        if os.environ.get("ENV") == "prod":
            # This is needed when we use KubernetesPodOperator and want to
            # share information via XCOM.
            with open("/airflow/xcom/return.json", "w") as f:
                json.dump(result, f)

if __name__ == "__main__":
    run()
