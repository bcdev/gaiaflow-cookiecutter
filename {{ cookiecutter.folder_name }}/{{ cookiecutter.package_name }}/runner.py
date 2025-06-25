# !!PLEASE DO NOT EDIT/DELETE THIS!!
# This file is the main entry point to your package when using Airflow to
# create DAGs from the task_factory.
# It imports the required function from your package and executes it with the
# arguments provided

import ast
import importlib
import json
import os

from airflow.models.taskinstance import TaskInstance
from airflow.utils.context import Context


def run(
    func_path: str | None = None,
    kwargs: dict[str, str] | None = None,
    xcom_pull_tasks: dict | None = None,
    **context: Context
) -> dict[str, str]:
    env = os.environ.get("ENV", "dev")
    print(f"## Runner running in {env} mode ##")
    if env == "dev":
        ti: TaskInstance = context.get("ti")
        if ti and xcom_pull_tasks:
            for arg_key, pull_config in xcom_pull_tasks.items():
                source_task = pull_config["task"]
                key = pull_config.get("key", "return_value")
                pulled_val = ti.xcom_pull(task_ids=source_task, key=key)
                kwargs[arg_key] = (
                    pulled_val
                    if not isinstance(pulled_val, dict)
                    else pulled_val.get(arg_key)
                )
            print(
                f"[XCom] [dev] Pulled {kwargs}"
            )
    else:
        xcom_pull_tasks = json.loads(os.environ.get("XCOM_PULL_TASKS", "{}"))
        func_path = os.environ.get("FUNC_PATH", "")
        kwargs = json.loads(os.environ.get("FUNC_KWARGS", "{}"))
        rendered_pull_results = json.loads(os.environ.get("XCOM_PULL_RESULTS", "{}"))

        print(f"[XCom] [prod] Pulled from env: {rendered_pull_results}")

        for arg_key, pull_config in xcom_pull_tasks.items():
            pulled_val = rendered_pull_results.get(pull_config["task"])
            if pulled_val:
                try:
                    pulled_val = ast.literal_eval(pulled_val)
                    if isinstance(pulled_val, dict):
                        kwargs[arg_key] = pulled_val.get(arg_key)
                    else:
                        kwargs[arg_key] = pulled_val
                except Exception as e:
                    print(f"[XCom] [prod] Failed to parse XCOM for {arg_key}: {e}")

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

    return result

if __name__ == "__main__":
    run()
