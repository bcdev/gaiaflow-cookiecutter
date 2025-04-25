import json
from airflow.operators.python import PythonOperator
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator

def task_factory(
    task_id: str,
    func_path: str,
    func_kwargs: dict = None,
    image: str = None,
    env: str = "dev",
    xcom_push: bool = True,
    xcom_pull_tasks: dict = None,
    secrets: list = None,
):
    if xcom_pull_tasks:
        for arg_key, pull_config in xcom_pull_tasks.items():
            source_task, key = pull_config["task"], pull_config.get("key", "return_value")
            func_kwargs[arg_key] = "{{ ti.xcom_pull(task_ids='" + source_task + "', key='" + key + "') }}"

    if env == "dev":
        from {{ cookiecutter.package_name }}.runner import run
        return PythonOperator(
            task_id=task_id,
            python_callable=run,
            op_kwargs={"func_path": func_path, "kwargs": func_kwargs},
            do_xcom_push=xcom_push,
        )
    elif env == "prod":
        return KubernetesPodOperator(
            task_id=task_id,
            name=task_id,
            image=image,
            cmds=["python", "-m", "{{ cookiecutter.package_name }}.runner"],
            env_vars={
                "FUNC_PATH": func_path,
                "FUNC_KWARGS": json.dumps(func_kwargs),
                "ENV": "prod"
            },
            secrets=secrets or [],
            get_logs=True,
            is_delete_operator_pod=True,
            in_cluster=True,
            do_xcom_push=xcom_push
        )

    else:
        raise ValueError(f"env can only be dev or prod, but got {env}")

