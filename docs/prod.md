# From Local DAGs to Production-Ready Workflows

Please make sure you have done the following things before proceeding:

1. You have created and tested your package.
2. You have created the DAGs using this package.
3. The Gaiaflow services are running.

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

In Windows:
```bash
set AIRFLOW_CONFIG=%cd%\airflow_test.cfg
```

In Linux:
```bash
export AIRFLOW_CONFIG=$(pwd)/airflow_test.cfg
```

```bash
pytest
```

To ignore the pre-written tests for managers, run:

```bash
pytest -m "not gaiaflow"
```

On windows, run pytest like this:
```bash
pytest --ignore=logs
```

Once the tests here are green, move to the next level of testing.

## Level 2: Test in the Airflow instance running on Docker Compose in `dev` mode

This will ensure the execution of your DAGs within the Docker Compose 
which is similar to the prod environment (although prod environment works 
with docker image, we will see that in Level 3). This will help catch any bugs 
in your overall task flow execution in the DAG and see if data is being passed
through one from task to another as expected locally using the `PythonOperator`.

First make sure that you set the environment to `dev` when using `task_factory`.

If you decided to use Airflow on your own during the project initialization, 
please make sure to use the dag with `PythonOperator` or any other operator 
that can be run locally but not the `KubernetesPodOperator`.

You can either run this command:

```bash
    docker compose exec airflow-scheduler airflow dags test <your-dag-id>
```

or trigger the dag from the UI.

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

## Level 3: Testing your DAG using Docker Images in `prod_local` mode

This is the last test before you can run your DAGs in production with peace in 
mind.

This will mimic how the tasks will run on the prodcution cluster. Each task
within the DAG will run separately. 

To test this, you would need to start the minikube cluster locally using
the `minikube_manager.py` provided.

To start minikube cluster,
```bash
python minikube_manager.py --start
```

This starts the cluster and also generates a `kube_config_inline` file that is 
required by airflow to know which minikube cluster to use.

You would then need to make the docker image 
available locally for the minikube cluster to be picked
up. 
A Dockerfile is already provided to create a docker image for your package.

To do so, run:
```bash
python minikube_manager.py --build-only
```

You are now ready for testing the dag locally in a production-like environment,
to do so, go the Airflow UI, and open your dag, check that the operator has now
changed to `KubernetesPodOperator`, then trigger it.

If you face any errors like no `kube_config` found, you would need
to restart your airflow services so that they can pick up the new 
`kube_config_inline` if it doesn't automatically. To do so, run:

```bash
python mlops_manager.py --restart --service airflow -b
```

Once this passes, you can be sure that your DAG would also work
in the production environment.

## BONUS testing

This is optional but in case you want to test each task separately using the 
docker image that you created, you can do so.

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

For moving into production, the [Centralized Dag Repository](https://github.com/bcdev/airflow-dags)
(CDR) must know that you exist and are interested in using the production 
airflow.
                  
To do so, do the following steps (keep in mind they only have to be done once
per project by any team member of that project)

- Make sure you change the `task_factory` mode to `prod`.
- Contact the CDR maintainers and ask them to add your repository as a 
  `submodule` (They will know what to do!)

  - Create a Personal Access Token from your account (make sure your account is a 
  member of the bcdev org for this to work).

       Do as follows:
  
       - Go to your Github account Settings
       - Navigate to `<> Developer Settings` (the last button on the page)
       - Create a `Personal access token (classic)`
       - See the image below for reference:
   
       - Only click on the `repo` permissions
       - Create the token
       - Copy and keep it safe somewhere (maybe on KeePassXC)
       - Now, navigate to your newly created project, create a new Secret
           - Go to Repository settings
             - Navigate to `Secrets and Variables -> Actions -> New repository secret`
             - In the `Name` field, insert `CDR_PAT`
             - In the `Secret` field, insert your token that generated a few moments ago
           - Click on `Add Secret`  

- Now you are ready to deploy your dags to the production Airflow.

- The CI to deploy your dags runs only when you create a new release of 
your project package. This has been done in order to make sure that each dag
that goes into production has a release tag to it. 
This will trigger the CI to 
dispatch an event to the CDR to let it know you are ready for loading and 
triggering your DAG(s) from the production deployment of Airflow at BC.


Your DAG will now visible in production Airflow, which you can trigger.