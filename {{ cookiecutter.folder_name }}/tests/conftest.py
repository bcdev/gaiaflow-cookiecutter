import os

def pytest_configure():
    os.environ['AIRFLOW_CONFIG'] = os.path.join(os.getcwd(), 'airflow_test.cfg')