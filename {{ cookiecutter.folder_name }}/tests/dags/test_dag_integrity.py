import logging

import pytest
from airflow.models import DagBag


@pytest.fixture(scope="module")
def dagbag():
    return DagBag()

def test_no_import_errors(dagbag):
    assert len(dagbag.import_errors) == 0, f"DAG import failures: {dagbag.import_errors}"

def test_dag_count(dagbag):
    assert len(dagbag.dags) > 0, "No DAGs were loaded."

@pytest.mark.parametrize("dag_id,dag", [(dag_id, dag) for dag_id, dag in DagBag().dags.items()])
def test_dag_in_detail(dag_id, dag):
    assert dag.description, f"DAG '{dag_id}' has no description."
    assert dag.tags, f"DAG '{dag_id}' has no tags."
    assert dag.catchup is False, f"DAG '{dag_id}' has catchup enabled."
    try:
        assert dag.schedule is not None, (
            f"DAG '{dag_id}' has no schedule."
        )
    except AssertionError:
        logging.warning(f"DAG '{dag_id}' has no schedule.")
    assert len(dag.tasks) > 0, f"DAG '{dag_id}' has no tasks."

    task_ids = [task.task_id for task in dag.tasks]
    assert len(task_ids) == len(set(task_ids)), (
        f"DAG '{dag_id}' has duplicate task IDs."
    )

    for task in dag.tasks:
        assert task.retries is not None, f"Task '{task.task_id}' in DAG '{dag_id}' has no retries set."
        assert task.retries > 2, f"Task '{task.task_id}' in DAG '{dag_id}' has retries <= 2."
