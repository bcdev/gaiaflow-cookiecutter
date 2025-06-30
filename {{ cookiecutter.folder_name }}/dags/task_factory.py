import json

from airflow.operators.python import PythonOperator
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client import V1EnvFromSource, V1SecretReference


def task_factory(
        task_id: str,
        func_path: str,
        func_kwargs: dict = None,
        image: str = None,
        env: str = "dev",
        xcom_push: bool = True,
        xcom_pull_tasks: dict = None,
        secrets: list = None,
        env_vars: dict = None,
):
    if func_kwargs is None:
        func_kwargs = {}

    full_kwargs = {
        "func_path": func_path,
        "kwargs": func_kwargs,
    }

    if xcom_pull_tasks:
        full_kwargs["xcom_pull_tasks"] = xcom_pull_tasks

    if env == "dev":
        from please_work.runner import run
        return PythonOperator(
            task_id=task_id,
            python_callable=run,
            op_kwargs=full_kwargs,
            do_xcom_push=xcom_push,
        )
    elif env == "prod" or env == "prod_local":
        if not image:
            raise ValueError(f"Docker image expected when in {env} mode")
        if env == "prod_local":
            in_cluster = False
        else:
            in_cluster = True
        if secrets:
            env_from = [V1EnvFromSource(secret_ref=V1SecretReference(
                name=secret)) for secret in secrets]
        else:
            env_from = None

        xcom_pull_results = {}

        for arg_key, pull_config in (xcom_pull_tasks or {}).items():
            source_task = pull_config["task"]
            key = pull_config.get("key", "return_value")
            xcom_pull_results[source_task] = (

                    "{{ ti.xcom_pull(task_ids='" + source_task + "', key='" + key + "') }}"

            )

        default_env_vars = {
            "FUNC_PATH": func_path,
            "FUNC_KWARGS": json.dumps(func_kwargs),
            "XCOM_PULL_TASKS": json.dumps(xcom_pull_tasks or {}),
            "XCOM_PULL_RESULTS": json.dumps(xcom_pull_results),
            "ENV": "prod",
        }

        if env_vars:
            env_vars.update(default_env_vars)

        return KubernetesPodOperator(
            task_id=task_id,
            name=task_id,
            image=image,
            cmds=["python", "-m", "please_work.runner"],
            env_vars=env_vars,
            env_from=env_from,
            get_logs=True,
            is_delete_operator_pod=True,
            log_events_on_failure=True,
            in_cluster=in_cluster,
            do_xcom_push=xcom_push,
        )

    else:
        raise ValueError(f"env can only be dev, prod_local or prod, but got"
                         f" {env}")
