# Getting Started with Airflow

Hey, welcome!

Here, we will learn how to define DAGs using Airflow.

Please use the `change_me_*` files to read the comments and understand how to create
DAGs.

## Some basics to understand the creation of Airflow DAGs

- `DAG - Directed Acyclic Graphs` -> collection of tasks with directional dependencies.
- `Pipeline/Workflow`             -> Same as DAG. You can call your DAG a pipeline or workflow.


- DAGs in airflow can triggered by defining the start_date and/or schedules (which can be manually triggered as well).
- For automatic triggers, defining the schedule is mandatory.
- For testing purposes, you can trigger them manually. If you would like to also manually trigger them for your workflow
you can!
- But if you want your DAG to run periodically, setting the start_date and schedule is important.
- NOTE: By default, if you set a `start_date` in the past, Airflow will try to backfill all those runs. To avoid that,
use catchup=False inside the dag definitions.


## Common parameters used while defining a DAG


- `description`                   -> description for the DAG to be shown on the webserver
- `start_date`                    -> The timestamp from which the scheduler will attempt to backfill the dag runs. Recommended to keep it
                                 the date when you would run it for the first time and don't change it.
- `schedule`                      -> Defines the rules according to which DAG runs are scheduled. Can accept cron string, timedelta object,
                                 Timetable, or list of Dataset objects. If this is not provided, the DAG will be set to the default
                                 schedule timedelta(days=1).
- `catchup`                       -> Perform scheduler catchup by backfilling runs (or only run latest)
- `task_groups`                   -> Used to organize tasks into hierarchical groups in Graph view.
- `tasks`                         -> The actual tasks that needs to run. Airflow by default provides several operators to run various types of
                                 tasks. For e.g., if you want to run a Bash operation, you can use the BashOperator, if you would like to
                                 run Python, use the PythonOperator. When and if this goes to production, we will use KubermetesPodOperator,
                                 but you dont have to worry about that now. Most likely for testing and running experiments locally, we
                                 recommend using BashOperator and PythonOperator. We have provided some examples below on how to use them.
- `dependencies`                  -> This basically defines the flow of your DAG i.e. which task is dependent on which. Be careful to
                                 avoid cyclic dependencies as this is supposed to be an acyclic graph.


If you find any errors or bugs, please let us know.