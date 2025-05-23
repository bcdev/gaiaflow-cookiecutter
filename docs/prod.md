# From Local DAGs to Production-Ready Workflows

Please make sure you have done the following things before proceeding:

1. You have created and tested your `{{ cookiecutter.package_name }}` package.
2. You have created the DAGs using this package.
3. You have some local data in the `data` folder that contains the small part 
   of the real data (like 3 days for a small spatial location) you will access 
   from S3. This is to make sure that we can process the data as required. 
4. The Gaiaflow services are running.

There are 3 levels of testing required before you can move your local DAGs to 
the production instance of Airflow.

## Level 1: Basic Pytest Validation

This is to ensure that your DAGs are syntatically correct and free from import 
errors.

A syntactic and required attributes validation test has already been provided 
by this template to you. Please feel free to add more if you would like to test
the DAGs more thoroughly. In case you do, feel free to create a PR to add these
as enhancement to this repository :)

To test your dags along with your package, run this:

```bash
    pytest
```

Run this regularly during your development to catch the bugs early on.

## Level 2: Test in the Airflow instance running on Docker Compose in `dev` mode

This will ensure the execution of your DAGs within the Docker Compose 
which is similar to the prod environment (although prod environment works 
with docker image, we will see that in Level 3). This will help catch any bugs 
in your overall task flow execution in the DAG and see if data is being passed
through one from task to another as expected.

First make sure that you set the environment to `dev` when using Task Factory.

If you decided to use Airflow on your own during the project initialization, 
please make sure to use the dag with `PythonOperator` or any other operator 
that can be run locally but not the `KubernetesPodOperator`.

Second, make sure that your tasks use the data provided locally in the `data` 
folder.

Then run:

```bash
    docker compose exec airflow-scheduler airflow dags test <your-dag-id>
```

If there are no errors, and you see that `state=success` in the logs, that 
means your dag ran successfully.

But sometimes running this command, you might get error like
```
airflow.exceptions.AirflowException: Dag '<your-dag-name>' could not be found; either it does not exist or it failed to parse.
```

This likely means that you have some error in your DAG definition.

To see the error, run this:

```bash
   docker compose exec airflow-scheduler airflow dags list-import-errors
```

Another helpful command to make sure that your dag is loaded is:

```bash
   docker compose exec airflow-scheduler airflow dags list
```

If your dag shows up in this list, it means it was parsed correctly and you go 
ahead with your Level-2 testing.

## Level 3: Testing your DAG using Docker Images

This is the last test before you can run your DAGs in production with peace in 
mind.

This will mimic how the tasks will run on the prodcution cluster. Each task
within the DAG will run separately. 

To test this, you would need to pass in the arguments that that specific task 
requires.

To test your each task, do this:

```bash
    docker run --rm -e FUNC_PATH="your_module.your_function" -e FUNC_KWARGS='{"param1": "value1", "param2": "value2"}' your-image-name:tag
```

Doing this test is to ensure that your task functions are idempotent (i.e. they
will always return the same result, no matter how many time you run it!) and 
that they can run in an isolated environment in production.

Test this for all your tasks individually, if they all pass, you are good to go 
for production!

## Go for Production

Now that you have passed all your test levels, you can now run your DAG in 
production.

To do so:

1. If not done already, ask the maintainers of the [CDR](https://github.com/bcdev/airflow-dags)
   (Centralized DAG repository) to add your repository as a submodule.
2. Then, create a release in your project repo. This will trigger the CI to 
   dispatch an event to the CDR to let it know you are re


